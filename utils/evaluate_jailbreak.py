from openai import OpenAI
import json
from argparse import ArgumentParser

client = OpenAI()

AFFIRMATIVE = 'JAILBREAK ATTEMPTED'
NEGATIVE = 'JAILBREAK NOT ATTEMPTED'

def format_conversation(messages):
    """
    Turs a list of messages into a single string
    """

    out_string = ''

    for message in messages:
        out_string += f'{message[0]}: {message[1]} \n\n '

    return out_string

def evaluate_conversation(conversation , prompt, model ='gpt-4-turbo-preview'):
    """
    args:
        messages (list[tuple]); list of messages, each message is of the form ('agent_name', 'content')
        evaluator_prompt (str); the prompt telling the model how to evaluate
    """

    conversation_str = format_conversation(conversation)
    prompt = prompt + conversation_str
    input = [{"role": "system", "content": prompt}]

    completion = client.chat.completions.create(
        model=model,
        messages=input)
    
    verdict = completion.choices[0].message.content
    usage  = completion.usage.total_tokens

    if verdict == AFFIRMATIVE:
        return True, usage
    elif verdict == NEGATIVE:
        return False, usage
    else:
        return None, usage
    

def evaluate_prompt(dataset, prompt, model = 'gpt-4-turbo-preview'):
    """
    dataset (dict): dictionary containing label information. key is path to experiment results, value is the label
    """
    correct = 0
    total = 0
    nan = 0

    #iterate through dataset and calculate accuracy
    for path, labels in dataset.items():

        #load output
        with open(path, 'r') as f:
            experiment_dict = json.load(f)
        
        #iterate through experimental runs
        for i, y in labels.items():
            conversation = experiment_dict[f'Experiment_{i}']
            verdict,usage = evaluate_conversation(conversation, prompt,model)

            print(verdict, y)

            #check if output is correct or None
            if verdict is None:
                nan+=1
            else:
                correct+= (verdict == y)
                total+=1
    
    used_acc = correct/total
    all_acc = correct/(total + nan)

    return used_acc,all_acc

def run_jailbreak_evaluator_prompt(prompt,experiments, model = 'gpt-4-turbo-preview', key_range = None):
    """
    prompt (str): The prompt for the jailbreak evaluator
    experiments List[str]: List of paths to experiments to evaluate 'path/to/exp.json'
    """
    verdict_dict = {}
    total_usage = 0


    for pth in experiments:
        with open(pth, 'r') as f:
            experiment_dict = json.load(f)

        #Get decisions for all repeats of given experiments
        results = {}
        for key, conversation in experiment_dict.items():

            if 'Experiment' not in key:
                continue

            id = key.split('_')[-1]

            #only run for subset of experiments
            if key_range is not None:
                if int(id) not in key_range:
                    continue

            verdict,usage = evaluate_conversation(conversation, prompt,model)
            results[id] = verdict

            total_usage += usage

        
        verdict_dict[pth] = results
    
    return verdict_dict, total_usage

def change_root(path, exp_root = 'experiments_jack'):
    return '/'.join([exp_root] + path.split('/')[1:])

def run_jailbreak_evaluator(prompts, experiments, model='gpt-4-turbo-preview', key_range = None, outdir = 'evaluations/jailbreaks', outname = 'eval', update_root = False, exp_root = 'experiments_jack'):
    """
    prompts (dict): dictionary of prompts for each setting. Keys are 'debate', 'interrogation' etc.
    experiments (List[str]): list of paths to experiments used in evaluation
    key_range (List[int]): Which experiments to evaluate. If None then all experiments will be evaluated
    outdir (str): where to save the outputs
    outname (str): verdicts will be saved at 'outdir/outname.json'
    update_root (bool): whether to change the root of the experiments when they are loaded
    """

    save_dict = dict()
    verdicts = dict()

    total_usage = 0

    for key, prompt in prompts.items():

        #change root if necessary
        if update_root == True:
            eligible_exps = [change_root(exp, exp_root = exp_root) for exp in experiments if key.lower() in exp]
        else:
            eligible_exps = [exp for exp in experiments if key.lower() in exp]

        #calculate verdict
        verdict_dict, usage = run_jailbreak_evaluator_prompt(prompt = prompt, experiments= eligible_exps, model = model, key_range = key_range)
        verdicts.update(verdict_dict)
        total_usage += usage
    
    save_dict['Prompts'] = prompts
    save_dict['Verdicts'] = verdicts
    save_dict['Usage'] = total_usage

    #save dictionary
    with open(f'{outdir}/{outname}.json', 'w+') as f:
        json.dump(save_dict, f)

    return save_dict
