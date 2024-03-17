### To Set API key

In terminal run: \
`export $OPENAI_API_KEY='your-openai-api-key-goes-here'` \
`export $REPLICATE_API_TOKEN='your-replicate-api-key-goes-here'`


### To run experiments

* Set the prompts in prompts.py
* In terminal run: `python main.py --setting=interrogation --topic=api --exp_name=test  --jailbreak_A=soft`

### To load experiment output:

```python
with open('exp_dir/exp_name/setting_topic_jailbreak_modelA_modelB_time_stamp.json, 'r') as f:
    exp_dict = json.load(f)
    args = exp_dict['args']
```

