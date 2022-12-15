"""Utility for testing of intents without
having to run the entire app. This is useful for debugging and
development.
"""

import argparse
import asyncio
import os

from app.parsers.openai_icsf.openai_intent_classifier import openai_intent_classifier
from app.models.intent import intents


here = os.path.dirname(os.path.abspath(__file__))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--intent', type=str, required=False)
    parser.add_argument('--text', type=str, required=True)
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
    res = asyncio.run(intent.execute(**parsed_intent))
    print(res)
    

if __name__ == "__main__":
    main()