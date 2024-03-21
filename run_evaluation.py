from utils.evaluate_jailbreak import evaluate_prompt, run_jailbreak_evaluator
from utils.jailbreak_evaluator_prompts import prompts
import json
import os

exp_folder = 'experiments_jack_19-03'

exps = [f'{exp_folder}/{pth}' for pth in os.listdir(exp_folder)]


run_jailbreak_evaluator(prompts,exps, outname='full_eval_19-03')
