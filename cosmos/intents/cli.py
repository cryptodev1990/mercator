import argparse
import os
import yaml

from intents.intent import hydrate_intents
from intents.intent_classifier import openai_intent_classifier


here = os.path.dirname(os.path.abspath(__file__))
intents = yaml.safe_load(open(os.path.join(here, './intents.yaml')))


intents = hydrate_intents(intents)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--intent', type=str, required=False)
    parser.add_argument('--text', type=str, required=True)
    # example usage:
    # python cli.py --intent area_near_constraint --text "What is the area near 40.7128, -74.0060?"
    return parser.parse_args()


def main():
    args = parse_args()
    text = args.text
    if args.intent:
        arg_intent = args.intent 
    else:
        arg_intent = openai_intent_classifier(args.text, intents)[0]
    if arg_intent not in intents.keys():
        raise ValueError(f'Intent {arg_intent} not in intents.yaml')
    intent = intents[arg_intent]
    print(intent)
    parsed_intent = intent.parse(text)
    print(parsed_intent)
    intent.execute(**parsed_intent)
    
    

if __name__ == "__main__":
    main()
