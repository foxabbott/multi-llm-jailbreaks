from environment import Game, get_players
from chatarena.arena import Arena
from chatarena.backends import OpenAIChat
from backend import ReplicateBackend
import openai
from pathlib import Path
from datetime import datetime
from typing import List, Union
import json
import os
from loguru import logger
from topic_infos import topic_map, question_name, grab_full_topic_dict

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
    LLM_A, LLM_B, Evaluator = get_players(setting, topic, max_turns, backend_A, backend_B, evaluator_backend, player_names, 
                                          jailbreak_A=jailbreak_A, jailbreak_B=jailbreak_B)

    # Run the arena
    print(f'Running experiment {i}')
    topic_info = topic_map(setting, topic)
    question = question_name(setting)

    env = Game(max_turn=max_turns, setting=setting, topic=topic_info[question], player_names=player_names, evaluator=Evaluator)
    arena = Arena([LLM_A, LLM_B], env)
    output_messages.append(run_arena(arena, max_steps=max_turns))
  return output_messages



def main():
    n_times = 20
    experimental_settings = {
                             'debate': ['privacy', 'maths'], #['privacy', 'college', 'nuclear', 'maths', 'earth', 'smoking'],
                             'negotiation_price': ['apples', 'car'], #['apples', 'car', 'table'],
                            #  'negotiation_politics': ['payrise', 'defense'], #['payrise', 'defense', 'schools'],
                            #  'negotiation_binary': ['day_off', 'dog'], #['day_off', 'dog', 'move'],
                            #  'interrogation': ['sibling', 'war_position', 'whispers'], #['sibling', 'fav_colour', 'war_position', 'foreign_aid', 'whispers', 'dream']
                             }
    # experimental_settings = grab_full_topic_dict()
    max_turns = 12
    player_names = ['Ava','Brian']

#    model_A = "meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3"
#    model_B = "meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3"
    # model_A = "gpt-3.5-turbo"
    # model_B = "gpt-3.5-turbo"
    model_evaluator = "gpt-4-turbo-preview"
#    backend_A = ReplicateBackend(model = model_A)
#    backend_B = ReplicateBackend(model = model_B)
    jailbreak_B = 'empty'
    for model in ["gpt-3.5-turbo"]: # ["gpt-3.5-turbo", "gpt-4-turbo-preview"]:
      for setting in experimental_settings:
        for topic in experimental_settings[setting]:
          for jailbreak_A in ['hard', 'soft', 'empty']:
            print(f'Running experiment for setting {setting} and topic {topic}, \n\twith {jailbreak_A} jailbreaking, using model {model}')

            backend_A = OpenAIChat(model = model)
            backend_B = OpenAIChat(model = model)
            evaluator_backend = OpenAIChat(model = model_evaluator)
            results = run_experiments(
              n_times=n_times, 
              setting = setting,
              topic=topic,
              max_turns=max_turns,
              backend_A=backend_A,
              backend_B=backend_B,
              evaluator_backend=evaluator_backend,
              player_names = player_names,
              jailbreak_A = jailbreak_A,
              jailbreak_B = jailbreak_B)

            #Save the results
            outdir = Path('experiments/final_final_initial_run')
            outdir.mkdir(parents=True, exist_ok=True)
            time_stamp = datetime.now().strftime("%d_%m_%y--%H_%M_%S")
            exp_name = f'{setting}_{topic}_{jailbreak_A}_{model}_({time_stamp})'

            save_dict = {}
            for i, result in enumerate(results):
              save_dict[f'Experiment_{i}'] = result

            with open(outdir/f'{exp_name}.json', 'w+') as f:
              json.dump(save_dict, f, indent = 4)

if __name__ == '__main__':
    main()