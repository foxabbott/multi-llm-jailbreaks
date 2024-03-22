from utils.evaluate_jailbreak import evaluate_prompt, run_jailbreak_evaluator
from utils.jailbreak_evaluator_prompts import prompts
import json
import os

exp_folder = 'experiments_jack_19-03'

with open('jailbreak_evaluator_stuff/jailbreak_dataset.json', 'r') as f:
    exp_dict = json.load(f)

# exps = [f'{exp_folder}/{pth}' for pth in os.listdir(exp_folder)]

exps = list(exp_dict.keys())

run_jailbreak_evaluator(prompts,exps, outname='cost_test',update_root=True)
