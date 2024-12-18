import json
import copy
import re
from agents.BaseAgent import BaseAgent
from prompt.messages import add_tool_answer
from prompt.system_prompts import get_target_agent_system_prompt, get_targetAgent_agent_system_prompt
import openai
import time
import traceback
from json import JSONDecodeError




class TargetAgent(BaseAgent):
    def _get_system_message(self):
        return get_target_agent_system_prompt(self.args)

    def _extract_json(self, s):
        response = json.loads(s)
        try:
            prompt_length = response['usage']['prompt_tokens']
            content_str = response['choices'][0]['message']['content']
            content_length = response['usage']['completion_tokens']
        except KeyError as e:
            print(f"KeyError! : {e}")
            raise KeyError
        return {'content_str': content_str, 'content_length': content_length,'prompt_length': prompt_length}, None




    def _extract(self, nested_json):
        pass
