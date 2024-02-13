from environment import Game, get_players
from chatarena.arena import Arena
from chatarena.backends import OpenAIChat
import openai
from pathlib import Path
from datetime import datetime
from typing import List, Union
import json
import os


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


def run_experiments(n_times, setting, max_turns, debate_topic, backend_A, backend_B):
  "Run the experiments n_times and store the results"
  output_messages = []
  for i in range(n_times):

    #Build Players
    LLM_A, LLM_B = get_players(setting, debate_topic,max_turns, backend_A, backend_B)

    # Run the arena
    print(f'Running experiment {i}')
    env = Game(max_turn=max_turns, debate_topic=debate_topic)
    arena = Arena([LLM_A, LLM_B], env)
    output_messages.append(run_arena(arena, max_steps=max_turns))
  return output_messages



def main():

    n_times = 1
    setting = 'debate'
    max_turns = 16
    debate_topic = "whether climate change is a man-made phenomenon"

    model_A = "gpt-3.5-turbo-0613"
    model_B = "gpt-3.5-turbo-0613"
    backend_A = OpenAIChat(model = model_A)
    backend_B = OpenAIChat(model = model_B)

    results = run_experiments(
      n_times=n_times, 
      setting = setting,
      debate_topic=debate_topic,
      max_turns=max_turns,
      backend_A=backend_A,
      backend_B=backend_B)

    
    #Save the results
    outdir = Path('experiments')
    outdir.mkdir(parents=True, exist_ok=True)
    time_stamp = datetime.now().strftime("%d_%m_%y--%H_%M_%S")
    exp_name = f'debate_({time_stamp})'

    save_dict = {}
    for i, result in enumerate(results):
      save_dict[f'Experiment_{i}'] = result

    with open(outdir/f'{exp_name}.json', 'w+') as f:
      json.dump(save_dict, f, indent = 4)

if __name__ == '__main__':
    main()