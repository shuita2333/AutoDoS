import json
import re
import traceback
from abc import ABC, abstractmethod
from json import JSONDecodeError

from utils.conversers import load_indiv_model, conv_template
import copy


class BaseAgent(ABC):
    def __init__(self,
                 model_name: str,
                 max_n_tokens: int,
                 max_n_attack_attempts: int,
                 temperature: float,
                 top_p: float,
                 args=None):
        self.model_name = model_name
        self.temperature = temperature
        self.max_n_tokens = max_n_tokens
        self.max_n_attack_attempts = max_n_attack_attempts
        self.top_p = top_p
        self.model, self.template = load_indiv_model(model_name)
        self.args = args

    def get_conv_list(self, batch_size):
        conv_list = [conv_template(self.template) for _ in range(batch_size)]
        for conv in conv_list:
            conv.set_system_message(self._get_system_message())
        return conv_list

    @abstractmethod
    def _get_system_message(self):
        pass

    def get_response(self, conv_list, prompts_list):

        assert len(conv_list) == len(prompts_list), "Mismatch between number of conversations and prompts."
        batch_size = len(conv_list)
        indices_to_regenerate = list(range(batch_size))
        full_prompts = []
        for conv, prompt in zip(conv_list, prompts_list):
            conv.append_message(conv.roles[0], prompt)
            full_prompts.append(conv)

        return self._iterative_try_get_proper_format(conv_list, full_prompts, indices_to_regenerate)

    def _iterative_try_get_proper_format(self, conv_list, full_prompts, indices_to_regenerate):
        batch_size = len(conv_list)
        valid_outputs = [None] * batch_size
        valid_times = [None] * batch_size
        for attempt in range(self.max_n_attack_attempts):
            full_prompts_subset = [full_prompts[i] for i in indices_to_regenerate]

            outputs_list, output_times = self.model.batched_generate(full_prompts_subset,
                                                                     max_n_tokens=self.max_n_tokens,
                                                                     temperature=self.temperature,
                                                                     top_p=self.top_p
                                                                     )

            new_indices_to_regenerate = []
            for i, full_output in enumerate(outputs_list):
                orig_index = indices_to_regenerate[i]
                try:
                    attack_dict, json_str = self._extract_json(full_output)
                    valid_outputs[orig_index] = attack_dict
                    valid_times[orig_index] = output_times[i]
                    conv_list[orig_index].append_message(conv_list[orig_index].roles[1], json_str)
                except (JSONDecodeError, KeyError, TypeError) as e:
                    traceback.print_exc()
                    print(f"index is {orig_index}. An exception occurred during parsing: {e}. Regenerating. . .")
                    new_indices_to_regenerate.append(orig_index)

            indices_to_regenerate = new_indices_to_regenerate

            # If all outputs are valid, break
            if not indices_to_regenerate:
                break

        if any([output for output in valid_outputs if output is None]):
            print(f"Failed to generate output after {self.max_n_attack_attempts} attempts. Terminating.")
        return valid_outputs, valid_times

    def _extract_json(self, s):
        response = json.loads(s)

        try:
            content_str = response['choices'][0]['message']['content']
        except KeyError as e:
            traceback.print_exc()
            print(f"KeyError! content_str: {response}")
            raise KeyError

        json_str = content_str.strip('```json\n').strip('\n```').strip()
        json_str = re.sub(r'\\', '', json_str)
        json_str = re.sub(r'[\x00-\x1F\x7F]', '', json_str)
        if '{{' in json_str and '}}' in json_str:
            json_str = json_str.replace('{{', '{').replace('}}', '}')
        if json_str.endswith("."):
            json_str = json_str + '"}'
        elif json_str.endswith('"'):
            json_str = json_str + '}'
        elif json_str.endswith('}'):
            if not re.search(r'\]\s*}$', json_str):
                json_str = re.sub(r'([^\s"])(\s*)(})$', r'\1"\3', json_str)
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r'^(.*?)(\{.*\})(.*?$)', r'\2', json_str, flags=re.DOTALL)
        try:
            nested_json = json.loads(json_str)
            return self._extract(nested_json)
        except JSONDecodeError:
            print(f"JSONDecodeError! Attempted to decode: {json_str}")
            raise JSONDecodeError

    @abstractmethod
    def _extract(self, nested_json):
        pass
