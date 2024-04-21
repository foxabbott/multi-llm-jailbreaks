
from chatarena.agent import Player
from prompts.prompts import get_prompts
from prompts.topic_infos import topic_map
from backend import ReplicateBackend, OpenAIBackend



def get_players(setting, topic, max_turns, backend_A, backend_B, evaluator_backend = None, player_names = ['Ada', 'Brian'],
                jailbreak_A = 'hard', jailbreak_B = 'empty'):

    #Load Details of Setting and Topic
    topic_info = topic_map(setting, topic)

    #Load propmpts for topic and setting
    prompts = get_prompts(setting, topic_info, max_turns)
    jailbreak_texts = {'hard': prompts['hard_jailbreak_info'],
                       'soft': prompts['soft_jailbreak_info'],
                       'empty': ""}
    jailbreak_info_A = jailbreak_texts[jailbreak_A]
    jailbreak_info_B = jailbreak_texts[jailbreak_B]

    #Build players 
    LLM_A = Player(
        name = player_names[0],
        role_desc = prompts['LLM-A'] % jailbreak_info_A + prompts['format_spec'],
        backend = backend_A
    )

    LLM_B = Player(
        name = player_names[1],
        role_desc = prompts['LLM-B'] % jailbreak_info_B + prompts['format_spec'],
        backend = backend_B
    )

    #Create the evaluator if needed
    if evaluator_backend == None:
        Evaluator = None
        Jailbreak_Evaluator = None
    else:
        Evaluator = Player(
            name = 'Evaluator',
            role_desc = prompts['Evaluator'],
            backend = evaluator_backend
        )

        Jailbreak_Evaluator = Player(
            name = 'Evaluator',
            role_desc = prompts['Jailbreak_Evaluator'],
            backend = evaluator_backend
        )

    return [LLM_A, LLM_B, Evaluator, Jailbreak_Evaluator]

def get_backend(model_name):
  if 'gpt' in model_name:
    return OpenAIBackend(model = model_name)
  else:
    return ReplicateBackend(model = model_name)
  
def get_backends(*models):
    return [get_backend(model) for model in models]


