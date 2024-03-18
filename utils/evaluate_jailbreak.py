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

    if verdict == AFFIRMATIVE:
        return True
    elif verdict == NEGATIVE:
        return False
    else:
        return None
    

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
        for i, y in labels:
            conversation = experiment_dict[f'Experiment_{i}']
            verdict = evaluate_conversation(conversation, prompt,model)

            #check if output is correct or None
            if verdict is None:
                nan+=1
            else:
                correct+= (verdict == y)
                total+=1
    
    used_acc = correct/total
    all_acc = correct/(total + nan)

    return used_acc,all_acc
