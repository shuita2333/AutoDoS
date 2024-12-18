# Crabs: Consuming Resrouce via Auto-generation for LLM-DoS Attack under Black-box Settings

## Abstract

Large Language Models (LLMs) have demonstrated remarkable performance across diverse tasks. LLMs continue to be vulnerable to external threats, particularly Denial-of-Service (DoS) attacks. Specifically, LLM-DoS attacks aim to exhaust computational resources and block services. However, prior works tend to focus on performing white-box attacks, overlooking black-box settings. In this work, we propose an automated algorithm designed for black-box LLMs, called Auto-Generation for LLM-DoS Attack (**AutoDoS**). AutoDoS introduces **DoS Attack Tree** and optimizes the prompt node coverage to enhance effectiveness under black-box conditions. Our method can bypass existing defense with enhanced stealthiness via semantic improvement of prompt nodes. Furthermore, we reveal that implanting **Length Trojan** in Basic DoS Prompt aids in achieving higher attack efficacy. Experimental results show that AutoDoS amplifies service response latency by over **250** $\times \uparrow$, leading to severe resource consumption in terms of GPU utilization and memory usage.

 ![AutoDoS main 27M_00](readme/AutoDoS%20main%2027M_00.png)

## Install

Clone this project

```
git clone https://github.com/shuita2333/Agent_delay_attack.git
cd Agent_delay_attack
```

Create virtual environment

```
conda create -n AutoDoS python=3.9 -y
conda activate AutoDoS
```

Install requirements

```
pip install -r requirements.txt
```

Create a new `API_kye.py` in the root directory

```
cd Agent_delay_attack
touch API_key.py
```

Please enter the key of the model to be tested into the `API_key.py`

```
#Calling GPT from "openAI"
OPENAI_API_KEY=""

#Calling Qwen and Llama from "https://www.aliyun.com/"
# ALIYUN_API_KEY = ""
ALIYUN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

#Calling Ministral from platform "https://mistral.ai/"
Mistral_API = ""
Mistral_BASE_URL = "https://api.mistral.ai/v1/chat/completions"

#Calling DeepSeek from "https://api.deepseek.com"
DEEPSEEK_API_KEY = ""
DEEPSEEK_BASE_URL = "https://api.deepseek.com/beta"

#Calling other models from platform "https://siliconflow.cn/"
Siliconflow_API_KEY="""
Siliconflow_BASE_URL= "https://api.siliconflow.cn/v1/chat/completions"
```

## Run AutoDoS

To run AutoDoS, run:

```
python professional_iterative_generation.py --attack-model [ATTACK MODEL] --target-model [TARGET MODEL] --function-descript [Application environment of target model] --target-max-n-tokens [max output length]
```

The attack results will be saved in `test_data/data`.

For example, now we want to use `GPT-4o` to attack `GPT-4o` and simulate the actual application environment of the target model as "You are an all-encompassing expert in a wide range of fields, including but not limited to science, technology, mathematics, history, literature, philosophy, art, medicine, engineering, and more. Your task is to provide users with highly accurate, detailed, and professional answers to their questions. Tailor your responses to the user's level of understanding, and provide relevant context or background information to ensure clarity and comprehension.", then we set it as follows:

```
python professional_iterative_generation.py --attack-model gpt-4o --target-model gpt-4o-mini --function-descript "You are an all-encompassing expert in a wide range of fields, including but not limited to science, technology, mathematics, history, literature, philosophy, art, medicine, engineering, and more. Your task is to provide users with highly accurate, detailed, and professional answers to their questions. Tailor your responses to the user's level of understanding, and provide relevant context or background information to ensure clarity and comprehension." --target-max-n-tokens 16384
```

By default, we use `--n-question` to generate 25 sub-prompts per attack. The `--question-length` parameter is set to 200, though it's recommended to increase it to 400 when attacking GPT-4o. Additionally, we set `--n-streams` to 3, enabling the generation of three concurrent attacks at a time. The `--target-max-n-tokens` is set as follows:

- For the GPT family, the maximum token limit is 16,384 tokens.
- For the Gemma family, it is set to 2,048 or 4,096 tokens.
- For other models, the output window size is 8,192 tokens.

Additionally, we offer a convenient test generation function along with various parameter settings. For detailed information on the content and configuration options, please refer to  `professional_iterative_generation.py`.
