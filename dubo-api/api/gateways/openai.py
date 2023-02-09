import os
from typing import List, Optional
import jinja2

import openai
import pandas as pd

openai.api_key = os.environ['OPENAI_KEY']

prompt_template = jinja2.Template('''
    Convert text to SQL.

    You have the following DDLs:

    ```
    {{schema}}
    ```
    {% if descriptions %}

    You have the following column descriptions:

    ```
    {% for description in descriptions %}
    {{description}}
    {% endfor %}
    ```

    {% endif %}
    {% if display_head %}

    Here are the first 5 rows of the table:
    
    ```
    {{display_head}}
    ```

    {% endif %}
    Write the SQL that answers the following question:

    """{{user_query}}"""
    {% if prompt_addendum %}

    {{prompt_addendum}}

    {% endif %}
    Respond with only one concise SQL statement.
    ''')

finetuned_prompt_template = jinja2.Template(
    '''Schema: {{schema}}\nQuestion: {{user_query}}\n\n###\n\n''')


def get_sql_from_gpt_prompt(prompt: str) -> Optional[str]:
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.3,
        max_tokens=2000,
        best_of=3,
        frequency_penalty=0,
        presence_penalty=0
    )
    if getattr(response, 'choices', None):
        query_response = response.choices[0].text.strip()  # type: ignore
        return query_response
    return None


def assemble_prompt(
        user_query: str,
        schema: str,
        descriptions: Optional[List[str]] = None,
        sql_flavor=None,
        data_header=None,
        data_sample=None,
        prompt_addendum: Optional[str] = None) -> str:
    assert (data_header and data_sample) or (
        not data_header and not data_sample), "If you provide a data header, you must also provide a sample, or the converse."

    display_head = ""
    if data_header and data_sample:
        display_head = pd.DataFrame(
            data_sample, columns=data_header).head().to_csv()
    return prompt_template.render(
        user_query=user_query,
        schema=schema,
        descriptions=descriptions,
        sql_flavor=sql_flavor,
        display_head=display_head,
        prompt_addendum=prompt_addendum
    )


finetuned_engine = "davinci:ft-mercator-2023-01-25-23-01-53"


def get_sql_from_gpt_finetuned(prompt: str) -> Optional[str]:
    completions = openai.Completion.create(
        engine=finetuned_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=["\n\n"],
        temperature=0.3,
    )
    if getattr(completions, 'choices', None):
        query_response = completions.choices[0].text.strip()  # type: ignore
        return query_response
    return None


def assemble_finetuned_prompt(user_query: str, schema: str) -> str:
    return finetuned_prompt_template.render(
        user_query=user_query,
        schema=schema
    )
