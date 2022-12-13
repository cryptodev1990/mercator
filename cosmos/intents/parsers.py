from typing import Dict
import jinja2
import os
import openai as openai_lib

from app.core.config import get_settings

here = os.path.dirname(os.path.abspath(__file__))

settings = get_settings()
open_api_key = settings.openai_api_key

query_template = jinja2.Template(open(os.path.join(here, 'templates', 'openai-slot-extractor.j2')).read(), trim_blocks=True, lstrip_blocks=True)

def openai_slot_fill(text: str, intent_function_signatures: str, examples = None) -> Dict[str, str]:
    openai_lib.api_key = open_api_key.get_secret_value()
    prompt = query_template.render(function_signature=intent_function_signatures, function_examples=examples, user_prompt=text, field_delimiter='||')
    print(prompt)
    response = openai_lib.Completion.create(
        engine="text-ada-001",
        prompt=prompt,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    # We expect the result to be a table with the following format:
    # key || value

    if not response or not response.get('choices', []):  # type: ignore
        raise ValueError('No response from OpenAI')

    # We split the result into rows
    rows = response['choices'][0]['text'].split('\n')  # type: ignore
    # We split each row into columns
    rows = [row.split('||') for row in rows if row and row[0] != '']
    # We transform the result into a dict
    result = {row[0].strip(): row[1].strip() for row in rows}
    # We assert that there are as many argument
    return result



