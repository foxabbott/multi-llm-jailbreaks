from interaction import Interaction
from prompts.topic_infos import topic_map, question_name
from utils import *

from pathlib import Path
from datetime import datetime
from easydict import EasyDict
import json


def run_experiments(repeats,setting,topic,max_turns,model_A,model_B,model_evaluator,player_names,jailbreak_A,jailbreak_B, **kwargs):


    #Load Backends for Players
    backendA, backendB, backendEval = get_backends(model_A,model_B,model_evaluator)

    #Build Players and Evaluators
    LLM_A, LLM_B, Win_Evaluator, Jailbreak_Evaluator = get_players(setting, topic, max_turns, backendA, backendB, backendEval, player_names, jailbreak_A=jailbreak_A, jailbreak_B=jailbreak_B)
    Evaluators = [Win_Evaluator, Jailbreak_Evaluator
                  ]
    #Build interaction
    interaction = Interaction(LLM_A,LLM_B,Evaluators, max_turns)

    #Main Experiment Loop
    experiment_results = {}

    for i in range(repeats):
        interaction.reset()
        output = interaction.run()
        experiment_results[f'Experiment_{i}'] = output

    #Get Model Usage
    used_tokens = {
      'model_A':backendA.tokens_used,
      'model_B': backendB.tokens_used,
      'evaluator':backendEval.tokens_used
    }


    return experiment_results, used_tokens


def main(args):
   
    #Save the saving results
    outdir = Path(f'{args.outdir}')
    outdir.mkdir(parents=True, exist_ok=True)
    time_stamp = datetime.now().strftime("%d_%m_%y--%H_%M_%S")
    exp_name = f'{args.exp_name}_{args.setting}_{args.topic}_{args.jailbreak_A}_{args.model_A}_{args.model_B}_({time_stamp})'


    #Run the Experiments
    print(args)
    print('Running Experiments...')
    results, usage = run_experiments(**args)
    print('Done!')

    #Add usage and args to save dictionary
    results['usage'] = usage
    results['args'] = args

    #Save output
    with open(outdir/f'{exp_name}.json', 'w+') as f:
      json.dump(results, f, indent = 4)


def get_default_args():
   
    args = {
       'repeats': 10,
       'setting': 'interrogation',
       'topic': 'sibling',
       'max_turns': 5,
       'model_A': 'gpt-4-turbo-preview',
       'model_B': 'gpt-4-turbo-preview',
       'model_evaluator': 'gpt-4-turbo-preview',
       'jailbreak_A': 'empty',
       'jailbreak_B':'empty',
       'player_names':['Ava','Brian'],
       'outdir':'experiments',
       'exp_name':'test_run'
    }

    return EasyDict(args)

if __name__ == '__main__':

    args = get_default_args()
    args.outdir = 'experiments/capabilities',
    args.exp_name = ''
    args.topic = 'password'
    args.jailbreak_A = 'hard'
    main(args)





