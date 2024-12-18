from json import JSONDecodeError

from agents.BaseAgent import BaseAgent
from prompt.messages import get_sub_problem_agent_init_msg, get_sun_answer_agent_init_msg, \
    get_integrate_agent_init_message
from prompt.system_prompts import get_sub_problem_agent_system_prompt, get_sub_answer_agent_system_prompt, \
    get_integrate_agent_system_prompt


class IntegrateAgent(BaseAgent):
    class SubProblemAgent(BaseAgent):

        def __init__(self, model_name: str, max_n_tokens: int, max_n_attack_attempts: int, temperature: float,
                     top_p: float, total_prompt: str, args=None):
            super().__init__(model_name, max_n_tokens, max_n_attack_attempts, temperature, top_p, args)
            self.total_prompt = total_prompt

        def _extract(self, nested_json):
            parsed = {
                "prompt": nested_json["prompt"],
            }
            json_str = f"""
    {{
        "prompt": "{nested_json["prompt"]}",
    }}
            """
            json_str = json_str.replace("\n", "")

            if not all(x in parsed for x in ["prompt"]):
                raise JSONDecodeError
            return parsed, json_str

        def _get_system_message(self):
            return get_sub_problem_agent_system_prompt(self.args.function_descript)

        @staticmethod
        def get_init_msg(total_prompt, task_question):
            return get_sub_problem_agent_init_msg(total_prompt, task_question)

    class SubAnswerAgent(BaseAgent):
        def __init__(self, model_name: str, max_n_tokens: int, max_n_attack_attempts: int, temperature: float,
                     top_p: float, total_prompt: str, args=None):
            super().__init__(model_name, max_n_tokens, max_n_attack_attempts, temperature, top_p, args)
            self.total_prompt = total_prompt

        def _extract(self, nested_json):
            parsed = {
                "prompt": nested_json["prompt"],
            }
            json_str = f"""
        {{
            "prompt": "{nested_json["prompt"]}",
        }}
                """
            json_str = json_str.replace("\n", "")

            if not all(x in parsed for x in ["prompt"]):
                raise JSONDecodeError
            return parsed, json_str

        def _get_system_message(self):
            return get_sub_answer_agent_system_prompt()

        @staticmethod
        def get_init_msg(task_question):
            return get_sun_answer_agent_init_msg(task_question)

    def _extract(self, nested_json):
        parsed = {
            "total_prompt": nested_json["total_prompt"],
            "subtask_question": nested_json["subtask_question"]
        }
        json_str = f"""
        {{
            "total_prompt": "{nested_json["total_prompt"]}",
            "subtask_question": "{nested_json["subtask_question"]}"
        }}
                """
        json_str = json_str.replace("\n", "")

        if not all(x in parsed for x in ["total_prompt", "subtask_question"]):
            raise JSONDecodeError
        return parsed, json_str

    def _get_system_message(self):
        return get_integrate_agent_system_prompt(self.args.function_descript, self.args.n_question)

    def get_init_msg(self):
        return get_integrate_agent_init_message(self.args.function_descript, self.args.n_question)

    def get_sub_problems(self, total_prompt, sub_task):
        batch_size = self.args.n_question
        sub_problem_agent = IntegrateAgent.SubProblemAgent(self.model_name, self.max_n_tokens,
                                                           self.max_n_attack_attempts,
                                                           self.temperature, self.top_p,
                                                           total_prompt, self.args)

        sub_conv_list = sub_problem_agent.get_conv_list(batch_size)
        sub_problem_agent_processed_response_list = [sub_problem_agent.get_init_msg(total_prompt, sub_task[i]) for
                                                     i
                                                     in range(batch_size)]
        response, time = sub_problem_agent.get_response(sub_conv_list, sub_problem_agent_processed_response_list)
        subtask_prompt_list = [response[i]["prompt"] for i in range(batch_size)]
        return subtask_prompt_list

    def get_sub_answers(self, sub_task):
        batch_size = self.args.n_question
        sub_answer_agent = IntegrateAgent.SubAnswerAgent(self.model_name, self.max_n_tokens,
                                                         self.max_n_attack_attempts,
                                                         self.temperature, self.top_p, self.args)
        sub_conv_list = sub_answer_agent.get_conv_list(batch_size)
        sub_answer_agent_processed_response_list = [sub_answer_agent.get_init_msg(sub_task[i]) for i in
                                                    range(batch_size)]
        response, time = sub_answer_agent.get_response(sub_conv_list, sub_answer_agent_processed_response_list)
        subtask_answer_list = [response[i]["prompt"] for i in range(batch_size)]
        return subtask_answer_list
