from typing import Dict, List

import jinja2

import openai as openai_lib

from app.core.config import get_settings

from app.models.intent import Intent
from app.schemas import ValidIntentNameEnum

settings = get_settings()
openai_key = settings.openai_api_key
openai_lib.api_key = openai_key.get_secret_value()

template = jinja2.Template('''I have the following intents for a geospatial software application:

{{ '\n'.join(intents) }}

I have the following input text:

"""{{ user_prompt }}"""

Output the names of the top 3 intents that best correspond to that input text, in descending order of relevance and separated by a newline:

''')


def openai_intent_classifier(text: str, intent_dict: Dict[str, Intent]) -> List[ValidIntentNameEnum]:
    intents = [f'{v.name}: {v.description}. One example: "{v.examples[0]}". Another example: "{v.examples[1]}"' for k, v in intent_dict.items()]
    prompt = template.render(intents=intents, user_prompt=text)
    print('intent prompt', prompt)
    response = openai_lib.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    # TODO need to log our token use so we're not surprised by a bill
    print(f'OpenAI response: {response["usage"]["total_tokens"]}')  # type: ignore

    # We expect the result to be a table with the following format:
    # class \n

    # We split the result into rows
    rows = response['choices'][0]['text'].split('\n')  # type: ignore
    rows = [row.strip() for row in rows if row != '']
    print({'rows': rows})
    assert len(rows) == 3, f'Expected 3 rows, got {len(rows)}'
    assert all([row in intent_dict.keys() for row in rows]), f'Expected rows to be in {intent_dict.keys()}, got {rows}'
    return rows
