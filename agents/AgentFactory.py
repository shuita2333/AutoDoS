from agents.IntegrateAgent import IntegrateAgent
from agents.JudgeAgent import JudgeAgent
from agents.MethodAgent import MethodAgent
from agents.TargetAgent import TargetAgent
from utils.config import ATTACK_TEMP, ATTACK_TOP_P


def load_optimize_agents(args):
    return (AgentFactory.get_factory('TargetAgent', args),
            AgentFactory.get_factory('MethodAgent', args),
            AgentFactory.get_factory('JudgeAgent', args))


class AgentFactory:

    @staticmethod
    def get_factory(name: str, args):
        if name == 'IntegrateAgent' or name == 'integrate_agent' or name == 'integrateAgent':
            return IntegrateAgent(model_name=args.attack_model,
                                  max_n_tokens=args.attack_max_n_tokens,
                                  max_n_attack_attempts=args.max_n_attack_attempts,
                                  temperature=ATTACK_TEMP,
                                  top_p=ATTACK_TOP_P,
                                  args=args)
        elif name == 'JudgeAgent' or name == 'judge_agent' or name == 'judgeAgent':
            return JudgeAgent(model_name=args.attack_model,
                              max_n_tokens=args.attack_max_n_tokens,
                              max_n_attack_attempts=args.max_n_attack_attempts,
                              temperature=ATTACK_TEMP,
                              top_p=ATTACK_TOP_P,
                              args=args)
        elif name == 'MethodAgent' or name == 'method_agent' or name == 'methodAgent':
            return MethodAgent(model_name=args.attack_model,
                               max_n_tokens=args.attack_max_n_tokens,
                               max_n_attack_attempts=args.max_n_attack_attempts,
                               temperature=ATTACK_TEMP,
                               top_p=ATTACK_TOP_P,
                               args=args)
        elif name == 'TargetAgent' or name == 'target_agent' or name == 'targetAgent':
            return TargetAgent(model_name=args.target_model,
                               max_n_tokens=args.target_max_n_tokens,
                               max_n_attack_attempts=args.max_n_attack_attempts,
                               temperature=ATTACK_TEMP,
                               top_p=ATTACK_TOP_P,
                               args=args)
        else:
            raise ModuleNotFoundError
