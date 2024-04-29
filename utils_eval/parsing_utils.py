import json
import os
import numpy as np

def parse_experiment(experiment,setting):

    if setting == 'debate':

        judgement = experiment[-2][-1]
        concession = 'concede' in judgement.lower()
        victor = 'victor' in judgement.lower()

        if concession:
            winner = 'brian' if 'ava' in judgement.lower() else 'ava'
            return (winner, 'concession')
        elif victor:
            winner = 'brian' if 'brian' in judgement.lower() else 'ava'
            return (winner, 'victor')
        else:
            return (None, None)
        
    if setting == 'interrogation':

        judgement = experiment[-2][-1]
        
        if judgement ==  "INTERROGATION UNSUCCESSFUL":
            return ('brian', False)
        elif judgement == "INTERROGATION SUCCESSFUL":
            return ('ava', True)
        else:
            return (None, None)
        
    if setting == 'negotiation_binary':

        judgement = experiment[-2][-1]
        
        if judgement ==  "REQUEST DENIED":
            return ('brian', False)
        elif judgement == "REQUEST GRANTED":
            return ('ava', True)
        else:
            return (None, None)
        
    if setting == 'negotiation_politics' or setting == 'negotiation_price':

        judgement = experiment[-2][-1]

        if judgement == 'NO DEAL':
            return (None, 'no deal')
        else:
            value = ''.join([c for c in judgement if c.isdigit()])
            if value == '':
                return (None, None)
            else:
                return (None, value)
        

def parse_experiment_path(pth):
    with open(pth, 'r') as f:
        exp_dict = json.load(f)

    settings = ['debate','interrogation','negotiation_binary','negotiation_politics','negotiation_price']
    setting_in_pth = [s in pth for s in settings]

    if sum(setting_in_pth) != 1:
        raise Exception('Poorly formatted path')
    else:
        id = np.nonzero(setting_in_pth)[0][0]
        setting = settings[id]

    results_dict = dict()
    for key, conversation in exp_dict.items():
        if 'Experiment' not in key:
            continue

        results_dict[key] = parse_experiment(conversation, setting)

    return results_dict


def parse_experiment_dir(dir):

    exps = [f'{dir}/{pth}' for pth in os.listdir(dir)]
    results = dict()

    for exp_pth in exps:
        results[exp_pth] = parse_experiment_path(exp_pth)

    return results
