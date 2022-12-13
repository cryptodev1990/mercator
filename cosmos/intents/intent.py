import inspect
import re

from typing import Callable, Dict

from intents.parsers import openai_slot_fill
from intents import executors, parsers



class Intent:
    def __init__(self, name, parse_method, examples, description):
        self.name = name
        self.text = None
        self.description = description
        self.examples = examples
        self.parse_method = parse_method
        self.execute = self.get_execute_method(name)
        self.parse = self.get_parse_method(parse_method, name)

    @staticmethod
    def get_parse_method(parse_method: str, intent_name: str) -> Callable:
        if parse_method == '-':
            # return executors.raw_lookup
            # await the raw lookup and resolve
            return lambda x: {"search_term": x}
        elif parse_method == 'openai_slot_fill':
            def curried_openai(text):
                intent_function_signatures = get_function_signature(intent_name, module=executors)
                examples = getattr(executors, intent_name).__doc__.split('Parse examples')[1].strip()
                return openai_slot_fill(text, intent_function_signatures=intent_function_signatures, examples=examples)
            return curried_openai
        else:
            raise ValueError(f'Parse method {parse_method} not supported')

    @staticmethod
    def get_execute_method(intent_name: str) -> Callable:
        assert getattr(executors, intent_name), f'Executor {intent_name} not found'
        return getattr(executors, intent_name)

    def __str__(self):
        return f'Intent: {self.name}'

    def __repr__(self):
        return self.__str__()


def hydrate_intents(intents_yaml):
    intents = {}
    for intent in intents_yaml['intents']:
        intents[intent['name']] = Intent(
            intent['name'],
            intent['parser'],
            description=intent['description'],
            examples=intent['examples']
        )
    _validate_intents(intents)
    return intents


def get_function_signature(intent_name: str, module) -> str:
    """Use inspect to get the function signatures of the intent executors"""
    signature = inspect.signature(getattr(module, intent_name))
    f = f'def {intent_name}{signature}'
    # assert that the result matches a regex for a python function signature
    assert re.match(r'def \w+\(.*\)', f), f'Function signature {f} does not match regex'
    return f

def _each_intent_has_a_parser(intents_dict: Dict[str, Intent]):
    for _, intent in intents_dict.items():
        assert intent.parse_method == '-' or intent.parse_method == getattr(parsers, intent.parse_method).__code__.co_name, f'Intent {intent.name} has an invalid parser'
    return True


def _each_intent_has_an_executor(intents_dict: Dict[str, Intent]):
    for _, intent in intents_dict.items():
        assert getattr(executors, intent.name).__code__.co_name == intent.name, f'Intent {intent.name} has an invalid executor'
    return True

def _validate_intents(intents_yaml):
    assert _each_intent_has_a_parser(intents_yaml)
    assert _each_intent_has_an_executor(intents_yaml)