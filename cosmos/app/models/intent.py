import os
import yaml
import inspect
import re

from typing import Any, Awaitable, Callable, Dict


from app.crud import executors
from app.schemas import ExecutorResponse


class Intent:
    def __init__(self, name, parse_method, examples, description):
        self.name = name
        self.text = None
        self.description = description
        self.examples = examples
        self.parse_method = parse_method
        self.execute = self.get_execute_method(name)
        # get number of slots in the execute method
        self.num_slots = len(inspect.signature(self.execute).parameters) - 1  # subtract 1 for conn
        # Kwargs in the signature for area_near_constraint, so we special-case it
        if name == 'area_near_constraint':
            self.num_slots -= 1
        self.parse = self.get_parse_method(parse_method, name)

    @staticmethod
    def get_parse_method(parse_method: str, intent_name: str) -> Callable[[str], Dict[str, str]]:
        if parse_method == '-':
            # return executors.raw_lookup
            # await the raw lookup and resolve
            return lambda x: {"search_term": x}
        elif parse_method == 'openai_slot_fill':
            def curried_openai(text):
                from app.parsers.openai_icsf import openai_slot_fill
                intent_function_signatures = funcs_for_openai(intent_name, module=executors)
                examples = getattr(executors, intent_name).__doc__.split('Parse examples')[1].strip()
                return openai_slot_fill(text, intent_function_signatures=intent_function_signatures, examples=examples)
            return curried_openai
        else:
            raise ValueError(f'Parse method {parse_method} not supported')

    @staticmethod
    # callable takes arbitrary arguments and returns a ExecutorResponse
    def get_execute_method(intent_name: str) -> Callable[..., Awaitable[ExecutorResponse]]:
        assert getattr(executors, intent_name), f'Executor {intent_name} not found'
        assert callable(getattr(executors, intent_name)), f'Executor {intent_name} not callable'
        # assert that one of the arguments is a database connection
        assert 'conn' in inspect.signature(getattr(executors, intent_name)).parameters.keys(), f'Executor {intent_name} does not have a database connection'
        return getattr(executors, intent_name)

    def __str__(self):
        return f'Intent: {self.name}'

    def __repr__(self):
        return self.__str__()


def hydrate_intents(intents_yaml) -> Dict[str, Intent]:
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


def funcs_for_openai(intent_name: str, module) -> str:
    """Use inspect to get the function signatures of the intent executors"""
    signature = inspect.signature(getattr(module, intent_name))
    f = f'def {intent_name}{signature}'
    # assert that the result matches a regex for a python function signature
    assert re.match(r'def \w+\(.*\)', f), f'Function signature {f} does not match regex'
    # We strip out the database connection info
    f = re.sub(r', conn: .*?AsyncConnection', '', f)
    # We strip out the return type
    f = re.sub(r' -> .*$', '', f)
    return f

def _each_intent_has_a_parser(intents_dict: Dict[str, Intent]):
    for _, intent in intents_dict.items():
        assert intent.parse_method == '-' or intent.parse_method == 'openai_slot_fill', f'Intent {intent.name} has an invalid parser'
    return True


def _each_intent_has_an_executor(intents_dict: Dict[str, Intent]):
    for _, intent in intents_dict.items():
        assert getattr(executors, intent.name).__code__.co_name == intent.name, f'Intent {intent.name} has an invalid executor'
    return True

def _validate_intents(intents_yaml):
    assert _each_intent_has_a_parser(intents_yaml)
    assert _each_intent_has_an_executor(intents_yaml)


here = os.path.dirname(os.path.abspath(__file__))
intents = yaml.safe_load(open(os.path.join(here, './intents.yaml')))
intents = hydrate_intents(intents)
intent_names = [intent.name for intent in intents.values()]

def create_intent_from_name(intent_name: str) -> Intent:
    """Create an intent object from a name and text"""
    assert intent_name in intent_names, f'Intent {intent_name} not found'
    intent = intents[intent_name]
    return intent
