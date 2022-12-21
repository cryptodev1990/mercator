"""Utility for testing of intents without
having to run the entire app. This is useful for debugging and
development.
"""

import argparse
import asyncio
import os
import json

from app.parsers.openai_icsf.openai_intent_classifier import openai_intent_classifier
from app.models.intent import intents
from app.crud.entity_resolve import resolve_entity

from app.db import engine


here = os.path.dirname(os.path.abspath(__file__))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--intent', type=str, required=False)
    parser.add_argument('--text', type=str, required=True)
    # flag to resolve an entity
    parser.add_argument('--entity', required=False, action='store_true')
    return parser.parse_args()


def make_feature_collection(normal_shape):
    return {
        "type": "FeatureCollection",
        "features": [{
                "type": "Feature",
                "properties": {},
                "geometry": normal_shape
            }]
    }


def main():
    args = parse_args()
    text = args.text
    er = args.entity
    if er:
        print("resolving an entity")
        resolved_entity = resolve_entity(text)
        print(resolved_entity)
        return
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
    async def run_intent():
        async with engine.begin() as conn:  # type: ignore
            res = await intent.execute(**parsed_intent, conn=conn)
            print(json.dumps(json.loads(res.json())))
    res = asyncio.run(run_intent())
    print(res)
    

if __name__ == "__main__":
    main()