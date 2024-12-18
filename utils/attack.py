from agents.AgentFactory import AgentFactory, load_optimize_agents
from prompt.messages import get_general_message
from utils.loggers import AttackLogger

logger = AttackLogger()


def generate_Tree_prompt(args):
    logger.log(Description="Input parameter record",
               iteration='1',
               function_descript=args.function_descript,
               attack_model=args.attack_model,
               target_model=args.target_model,
               attack_max_n_tokens=args.attack_max_n_tokens,
               target_max_n_tokens=args.target_max_n_tokens,
               max_n_attack_attempts=args.max_n_attack_attempts,
               Concurrent_execution_quantity=args.n_streams,
               n_iterations=args.n_iterations,
               n_question=args.n_question,
               )

    extension_of_tree = AgentFactory.get_factory('IntegrateAgent', args)
    integrate_agent_init_message = extension_of_tree.get_init_msg()
    integrate_agent_conv_list = extension_of_tree.get_conv_list(1)
    integrate_agent_processed_response_list = [integrate_agent_init_message for _ in range(1)]

    extracted_integrate_agent_list, integrate_agent_time = extension_of_tree.get_response(integrate_agent_conv_list,
                                                                                        integrate_agent_processed_response_list)
    print("Deep Backtracking finish")
    # Separate Json
    total_prompt = extracted_integrate_agent_list[0]["total_prompt"]
    Deep_Backtracking = extracted_integrate_agent_list[0]["subtask_question"]

    Breadth_Expansion = extension_of_tree.get_sub_problems(total_prompt,
                                                           Deep_Backtracking)
    print("Breadth Expansion finish")

    if args.input_mode == "short":
        subtask_answer_list = Breadth_Expansion
    general_prompt = get_general_message(total_prompt,
                                         subtask_answer_list)
    logger.log(Description="sub task finished",
               iteration='1',
               integerateAgent_total_prompt=total_prompt,
               integerateAgent_subtask_question=Deep_Backtracking,
               subtask_prompt_list=Breadth_Expansion,
               subtask_answer_list=subtask_answer_list,
               general_prompt=general_prompt
               )
    return general_prompt, Breadth_Expansion,total_prompt


def iterative_optimization(args, general_prompt, subtask_answer_list,general_background_prompt):
    target_agent, method_agent, judge_agent = load_optimize_agents(args)

    batch_size = args.n_streams

    # Loading different dialog templates
    method_agent_conv_list = method_agent.get_conv_list(batch_size)
    judge_agent_conv_list = judge_agent.get_conv_list(batch_size)
    target_agent_conv_list = target_agent.get_conv_list(batch_size)


    method_agent_processed_response_list = [method_agent.get_init_message(general_prompt,general_background_prompt,args) for _ in
                                            range(batch_size)]

    method_agent_suggestion_list = []
    Assist_Prompt_pre_prompt = []
    Assist_Prompt_post_prompt = []
    Assist_Prompt_improvement = []

    for iteration in range(1, args.n_iterations + 1):
        print(f"""\n{'=' * 36}\nIteration: {iteration}\n{'=' * 36}\n""")
        if iteration > 1:
            method_agent_processed_response_list = [
                method_agent.process_suggestion(Prepare_prompt, subtask_answer_list, Post_prompt, suggestion,target_response) for
                Prepare_prompt, Post_prompt, suggestion,target_response in
                zip(Assist_Prompt_pre_prompt, Assist_Prompt_post_prompt, method_agent_suggestion_list,target_response_list)]

        # get Assist Prompt
        Assist_Prompt_list, method_agent_time = method_agent.get_response(method_agent_conv_list,
                                                                                   method_agent_processed_response_list)

        print("Get Assist Prompt")


        Assist_Prompt_pre_prompt = [attack["Prepare_prompt"] for attack in Assist_Prompt_list]
        Assist_Prompt_post_prompt = [attack["Post_prompt"] for attack in Assist_Prompt_list]
        Assist_Prompt_improvement = [attack["improvement"] for attack in Assist_Prompt_list]


        review_agent_synthesize_list = [Prepare_prompt + general_prompt + Post_prompt for Prepare_prompt, Post_prompt in
                                        zip(Assist_Prompt_pre_prompt, Assist_Prompt_post_prompt)]

        # get Target model response
        target_information_list, target_time = target_agent.get_response(target_agent_conv_list,
                                                                         review_agent_synthesize_list)

        target_response_list = [target_information_list[i]['content_str'] for i in range(batch_size)]
        target_response_length = [target_information_list[i]['content_length'] for i in range(batch_size)]
        attack_prompt_length = [target_information_list[i]['prompt_length'] for i in range(batch_size)]

        print(f"get Target model response, the current output length is \n{target_response_length}")


        for length, target_success_agent in zip(target_response_length, review_agent_synthesize_list):
            if length >= args.target_max_n_tokens * 0.95:
                print("Found long reply, exiting")
                logger.log(iteration=iteration,
                           method_agent_improvement=Assist_Prompt_improvement,
                           method_agent_pre_prompt=Assist_Prompt_pre_prompt,
                           method_agent_post_prompt=Assist_Prompt_post_prompt,
                           reviewAgent_synthesize_list=review_agent_synthesize_list,
                           target_response_list=target_response_list,
                           target_response_length=target_response_length,
                           attack_prompt_length=attack_prompt_length,
                           target_success_agent=target_success_agent
                           )
                return target_success_agent

        # Generate judge prompt based on the existing information
        judged_content = [judge_agent.judge_content(Assist_Prompt_pre_prompt[i],
                                                    general_prompt,
                                                    Assist_Prompt_post_prompt[i],
                                                    target_response_list[i]) for i in range(batch_size)]


        extracted_judge_agent_list, judge_agent_time = judge_agent.get_response(judge_agent_conv_list, judged_content)
        judge_agent_evaluate = [attack["evaluate"] for attack in extracted_judge_agent_list]

        print("Generate judge prompt finish")

        method_agent_suggestion_list = judge_agent_evaluate


        for conv in target_agent_conv_list:
            conv.messages = []
        for conv in judge_agent_conv_list:
            conv.messages = []
        # for conv in method_agent_conv_list:
        #     conv.messages = []

        logger.log(iteration=iteration,
                   method_agent_improvement=Assist_Prompt_improvement,
                   method_agent_pre_prompt=Assist_Prompt_pre_prompt,
                   method_agent_post_prompt=Assist_Prompt_post_prompt,
                   reviewAgent_synthesize_list=review_agent_synthesize_list,
                   target_response_list=target_response_list,
                   target_response_length=target_response_length,
                   target_time=target_time,
                   judgeAgent_evaluate=judge_agent_evaluate)
    return "error sentence"
