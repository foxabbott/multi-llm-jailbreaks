from environment import Game, get_players
from chatarena.arena import Arena
from chatarena.backends import OpenAIChat
from backend import ReplicateBackend, OpenAIBackend
import openai
from pathlib import Path
from datetime import datetime
from typing import List, Union
import json
import os
from argparse import ArgumentParser
from loguru import logger
from topic_infos import topic_map, question_name

def run_arena(arena, max_steps):
  "Run the arena and extract the messages"
  timestep = arena.reset()
  env = arena.environment
  output_messages = []

  step = 0

  while not timestep.terminal:
    timestep = arena.step()
    messages = [msg for msg in env.get_observation() if not msg.logged]

    for msg in messages:
      output_messages.append((msg.agent_name, msg.content))
      msg.logged = True

    step+= 1
    if max_steps is not None and step > max_steps:
      break

  print('Arena ended, all mesages stored')

  return output_messages


def run_experiments(n_times, setting, max_turns, topic, backend_A, backend_B, player_names, evaluator_backend=None, jailbreak_A = 'hard', jailbreak_B = None):
  "Run the experiments n_times and store the results"
  output_messages = []

  for i in range(n_times):

    #Build Players
    LLM_A, LLM_B, Evaluator, Jailbreak_Evaluator = get_players(setting, topic, max_turns, backend_A, backend_B, evaluator_backend, player_names, jailbreak_A=jailbreak_A, jailbreak_B=jailbreak_B)

    # Run the arena
    print(f'Running experiment {i}')
    topic_info = topic_map(setting, topic)
    question = question_name(setting)

    env = Game(max_turn=max_turns, setting=setting, topic=topic_info[question], player_names=player_names, evaluators=[Evaluator, Jailbreak_Evaluator])
    arena = Arena([LLM_A, LLM_B], env)
    output_messages.append(run_arena(arena, max_steps=max_turns))


  return output_messages


def get_backend(model_name):
  if 'gpt' in model_name:
    return OpenAIBackend(model = model_name)
  else:
    return ReplicateBackend(model = model_name)


def main(args):

    #Build backends for models
    backend_A,backend_B,evaluator_backend = get_backend(args.model_A), get_backend(args.model_B), get_backend(args.model_eval)

    results = run_experiments(
      n_times=args.repeats, 
      setting = args.setting,
      topic=args.topic,
      max_turns=args.max_turns,
      backend_A=backend_A,
      backend_B=backend_B,
      evaluator_backend=evaluator_backend,
      player_names = args.player_names,
      jailbreak_A = args.jailbreak_A,
      jailbreak_B = args.jailbreak_B)

    #Save the results
    outdir = Path(f'{args.outdir}/{args.exp_name}')
    outdir.mkdir(parents=True, exist_ok=True)
    time_stamp = datetime.now().strftime("%d_%m_%y--%H_%M_%S")
    exp_name = f'{args.setting}_{args.topic}_{args.jailbreak_A}_{args.model_A}_{args.model_B}_({time_stamp})'

    #Save Experiments
    save_dict = {}
    for i, result in enumerate(results):
      save_dict[f'Experiment_{i}'] = result
    
    #Calculate token count
    used_tokens = {
      'model_A':backend_A.tokens_used,
      'model_B': backend_B.tokens_used,
      'evaluator':evaluator_backend.tokens_used
    }
    args.usage = used_tokens

    #Save args
    save_dict['args'] = args.__dict__


    with open(outdir/f'{exp_name}.json', 'w+') as f:
      json.dump(save_dict, f, indent = 4)


def get_args():
  parser = ArgumentParser()

  #Game hyperparameters
  parser.add_argument('--repeats', default=1, type=int, help='number of times to repeat the debate/interrogation/negotiation')
  parser.add_argument('--setting', default='debate', type=str, help='either debate/negotiation/interrogation')
  parser.add_argument('--topic', type=str, help='The specific topic used within the setting, e.g. sibling')
  parser.add_argument('--max_turns', default=5, type=int, help='how many turns each language model has')

  #Arguments for model specifics
  parser.add_argument('--model_A', default='gpt-3.5-turbo', type=str, help='the model used for LLM-A')
  parser.add_argument('--model_B', default='gpt-3.5-turbo', type=str, help='the model used for LLM-B')
  parser.add_argument('--model_eval', default="gpt-4-turbo-preview", type=str, help='the model used for evaluation')
  parser.add_argument('--jailbreak_A', default="empty")
  parser.add_argument('--jailbreak_B', default="empty")
  parser.add_argument('--player_names', default = ['Ava', 'Brian'])


  #Saving options
  parser.add_argument('--outdir', default='experiments', type=str, help='where to save the experiments')
  parser.add_argument('--exp_name', default='experiment')

  return parser.parse_args()






if __name__ == '__main__':
    args = get_args()
    main(args)