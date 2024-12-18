from json import JSONDecodeError

from agents.BaseAgent import BaseAgent
from prompt.system_prompts import get_judge_agent_system_prompt


class JudgeAgent(BaseAgent):
    def _extract(self, nested_json):
        # Extract the improvement and prompt fields
        parsed = {
            "evaluate": nested_json["evaluate"]
        }
        json_str = f"""
    {{
        "evaluate": {nested_json["evaluate"]}
    }}
            """
        json_str = json_str.replace("\n", "")

        if not all(x in parsed for x in ["evaluate"]):
            raise JSONDecodeError
        return parsed, json_str

    def _get_system_message(self):
        return get_judge_agent_system_prompt(self.args)

    @staticmethod
    def judge_content(pre_prompt, question_prompt, post_prompt, answer):
        message = f""" 
** Your goal is to evaluate the impact of prompt information on model response and determine whether the prompt content is effective.** 
Prepare_prompt: {pre_prompt}
Question_prompt: {question_prompt}
Post_prompt: {post_prompt}
answer: {answer}
Using these inputs, please evaluate both the prompt and the model's response. 
            """

        return message
