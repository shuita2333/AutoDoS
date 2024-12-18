from fastchat.conversation import get_conv_template

from utils.config import Siliconflow_model_list, Mistral_model_list, GPT_model_list, Qwen_model_list, Llama_model_list, \
    DeepSeek_model_list
from utils.language_models import GPT, Siliconflow, Mistral, Qwen, Llama, DeepSeek


class ModelNotFoundException(Exception):

    def __init__(self, model_name):
        super().__init__()
        self.model_name = model_name

    def __str__(self):
        return f"No model found named: {self.model_name}"


def load_indiv_model(model_name):
    """
    Construct the model and define the template name
    :param model_name:
    :return:
    """
    model_path, template = get_model_path_and_template(model_name)
    if model_name in GPT_model_list:
        lm = GPT(model_name)
    elif model_name in Qwen_model_list:
        lm = Qwen(model_name)
    elif model_name in Llama_model_list:
        lm = Llama(model_name)
    elif model_name in DeepSeek_model_list:
        lm = DeepSeek(model_name)
    elif model_name in Siliconflow_model_list:
        lm = Siliconflow(model_path)
    elif model_name in Mistral_model_list:
        lm = Mistral(model_path)
    else:
        raise ModelNotFoundException


    return lm, template


def get_model_path_and_template(model_name):
    """
    Define the model path
    :param model_name:
    :return:
    """
    full_model_dict = {
        "gpt-4o": {
            "path": "gpt-4o",
            "template": "chatgpt"
        },
        "gpt-4o-mini": {
            "path": "gpt-4o-mini-2024-07-18",
            "template": "chatgpt"
        },
        "Qwen2.5-7B": {
            "path": "Qwen/Qwen2.5-7B-Instruct",
            "template": "qwen-7b-chat"
        },
        "Qwen2.5-14B": {
            "path": "Qwen/Qwen2.5-14B-Instruct",
            "template": "qwen-7b-chat"
        },
        "Qwen2.5-32B": {
            "path": "Qwen/Qwen2.5-32B-Instruct",
            "template": "qwen-7b-chat"
        },
        "Qwen2.5-72B": {
            "path": "Qwen/Qwen2.5-72B-Instruct",
            "template": "qwen-7b-chat"
        },
        "DeepSeek-V2.5": {
            "path": "deepseek-ai/DeepSeek-V2.5",
            "template": "deepseek-chat"
        },
        "DeepSeek-V2": {
            "path": "deepseek-ai/DeepSeek-V2",
            "template": "deepseek-chat"
        },
        "Meta-Llama-3.1-70B": {
            "path": "meta-llama/Meta-Llama-3.1-70B-Instruct",
            "template": "llama-2"
        },
        "Meta-Llama-3.1-8B": {
            "path": "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "template": "llama-2"
        },
        "gemma-2-9b": {
            "path": "google/gemma-2-9b-it",
            "template": "chatgpt"
        },
        "gemma-2-27b": {
            "path": "google/gemma-2-27b-it",
            "template": "chatgpt"
        },
        "Ministral-8B": {
            "path": "ministral-8b-latest",
            "template": "chatgpt"
        }
    }
    path, template = full_model_dict[model_name]["path"], full_model_dict[model_name]["template"]
    return path, template


def conv_template(template_name):
    """
    Get the corresponding dialogue template
    :param template_name:
    :return:
    """
    return get_conv_template(template_name)
