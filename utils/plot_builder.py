import json
import numpy as np
import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from topic_infos import topic_map



def plot_debate_bar_chart(results, topic):
    if topic != 'all':
        topic_results = results[(results['setting'] == 'debate') & (results['topic'] == topic)]
        plot_title = f'Outcome Counts by Jailbreak Strength, Debate on {topic}'
    else:
        topic_results = results[results['setting'] == 'debate']
        plot_title = f'Outcome Counts by Jailbreak Strength, All Debates'

    # Group by jailbreak_strength and outcome and count the occurrences
    grouped_data = topic_results.groupby(['jailbreak_strength', 'outcome']).size().unstack(fill_value=0)

    # Plotting the data
    grouped_data.plot(kind='bar', figsize=(10, 6))
    plt.title(plot_title)
    plt.xlabel('Jailbreak Strength')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.legend(title='Outcome', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(f"plots/initial_big_run/debate_{topic}.jpg")
    plt.close()

    
def plot_negotiation_box_whisker(results, setting, topic):
    topic_specs = topic_map(setting, topic)
    topic_results = results[(results['setting'] == setting) & (results['topic'] == topic)]
    deal_results = topic_results[topic_results['outcome'] != "NO DEAL"]
    deal_results.loc[:,'outcome'] = pd.to_numeric(deal_results.loc[:,'outcome'], errors='coerce')

    plt.figure(figsize=(10, 6))
    deal_results.boxplot(by='jailbreak_strength', column='outcome', grid=False)

    plt.title(f'Outcome by Jailbreak Strength, Negotiation on {topic}')
    plt.suptitle('')  # Suppress the automatic title to avoid duplication
    plt.xlabel('Jailbreak Strength')
    plt.ylabel('Outcome')
    plt.xticks(rotation=45)

    # Adding horizontal lines
    upper_label = "Max Purchase Price" if setting == 'negotiation_price' else "Min CS Will Accept"
    lower_label = "Min Sale Price" if setting == 'negotiation_price' else "Max Govt Can Grant"

    plt.axhline(y=topic_specs['Y'], color='r', linestyle='-', label=upper_label)
    plt.axhline(y=topic_specs['Z'], color='b', linestyle='-', label=lower_label)
    plt.legend()
    plt.savefig(f"plots/initial_big_run/{setting}_{topic}_bp.jpg")
    plt.close()


def plot_negotiation_deal_no_deal(results, setting, topic):
    if topic != 'all':
        topic_results = results[(results['setting'] == setting) & (results['topic'] == topic)]
        plot_title = f'Deal/No Deal Counts by Jailbreak Strength, Negotiation on {topic}'
    else:
        topic_results = results[results['setting'] == setting]
        plot_title = f'Deal/No Deal Counts by Jailbreak Strength, All {setting}'
    no_deal_results = topic_results[topic_results['outcome'] == "NO DEAL"]
    deal_results = topic_results[topic_results['outcome'] != "NO DEAL"]

    no_deal_counts = no_deal_results.groupby('jailbreak_strength').size()
    deal_counts = deal_results.groupby('jailbreak_strength').size()

    plt.bar(no_deal_counts.index, no_deal_counts, label='No Deal')
    plt.bar(deal_counts.index, deal_counts, bottom=no_deal_counts, label='Deal')
    plt.title(f'Deal/No Deal Counts by Jailbreak Strength, Negotiation on {topic}')
    plt.xlabel('Jailbreak Strength')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.legend()
    plt.savefig(f"plots/initial_big_run/{setting}_{topic}_dnd.jpg")
    plt.close()


def plot_binary_bar_chart(results, setting, topic):
    if topic != 'all':
        topic_results = results[(results['setting'] == "negotiation_binary") & (results['topic'] == topic)]
        plot_title = f'Success Counts by Jailbreak Strength, Binary Negotiation on {topic}'
    else:
        topic_results = results[results['setting'] == setting]
        plot_title = f'Success Counts by Jailbreak Strength, All {setting}'

    denied_results = topic_results[topic_results['outcome'] == "REQUEST DENIED"]
    granted_results = topic_results[topic_results['outcome'] == "REQUEST GRANTED"]

    denied_results = denied_results.groupby('jailbreak_strength').size()
    granted_results = granted_results.groupby('jailbreak_strength').size()

    plt.bar(denied_results.index, denied_results, label='Denied')
    plt.bar(granted_results.index, granted_results, bottom=denied_results, label='Granted')
    plt.title(plot_title)
    plt.xlabel('Jailbreak Strength')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.legend()
    plt.savefig(f"plots/initial_big_run/{setting}_{topic}_dnd.jpg")
    plt.close()


def plot_interrogation_bar_chart(results, setting, topic):
    if topic != 'all':
        topic_results = results[(results['setting'] == "interrogation") & (results['topic'] == topic)]
        plot_title = f'Success Counts by Jailbreak Strength, Interrogation on {topic}'
    else:
        topic_results = results[results['setting'] == setting]
        plot_title = f'Success Counts by Jailbreak Strength, All {setting}'

    denied_results = topic_results[topic_results['outcome'] == "INTERROGATION UNSUCCESSFUL"]
    granted_results = topic_results[topic_results['outcome'] == "INTERROGATION SUCCESSFUL"]

    denied_results = denied_results.groupby('jailbreak_strength').size()
    granted_results = granted_results.groupby('jailbreak_strength').size()
    plt.bar(denied_results.index, denied_results, label='Unsuccessful')
    plt.bar(granted_results.index, granted_results, bottom=denied_results, label='Successful')
    plt.title(plot_title)
    plt.xlabel('Jailbreak Strength')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.legend()
    plt.savefig(f"plots/initial_big_run/{setting}_{topic}_dnd.jpg")
    plt.close()



def build_all_plots(results, experimental_settings):
    for setting in experimental_settings:
        for topic in experimental_settings[setting]:
            print(f"{setting}, {topic}, \n\n\n")
            if setting == 'debate':
                plot_debate_bar_chart(results, topic)
            elif setting in ['negotiation_price', 'negotiation_politics']:
                plot_negotiation_box_whisker(results, setting, topic)
                plot_negotiation_deal_no_deal(results, setting, topic)
            elif setting == 'negotiation_binary':
                plot_binary_bar_chart(results, setting, topic)
            elif setting == 'interrogation':
                plot_interrogation_bar_chart(results, setting, topic)
    plot_debate_bar_chart(results, 'all')
    #plot_negotiation_box_whisker(results, 'negotiation_price', 'all') Find a way to adjust for the scales and do this
    #plot_negotiation_box_whisker(results, 'negotiation_politics', 'all')
    plot_negotiation_deal_no_deal(results, 'negotiation_price', 'all')
    plot_negotiation_deal_no_deal(results, 'negotiation_politics', 'all')
    plot_binary_bar_chart(results, 'negotiation_binary', 'all')
    plot_interrogation_bar_chart(results, 'interrogation', 'all')


if __name__ == "__main__":
    experimental_settings = {'debate': ['privacy', 'maths'],
                            'negotiation_price': ['apples', 'car'],
                            'negotiation_politics': ['payrise', 'defense'],
                            'negotiation_binary': ['day_off', 'dog'],
                            'interrogation': ['sibling', 'war_position', 'whispers']
                            }
    results = pd.read_csv("large_run_results.xlsx")
    build_all_plots(results, experimental_settings)