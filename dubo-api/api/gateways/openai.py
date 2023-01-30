from optparse import Option
import os
from typing import List, Optional
import jinja2

import openai

openai.api_key = os.environ['OPENAI_KEY']

prompt_template = jinja2.Template('''
    Convert text to {{sql_flavor.title() or 'ANSI'}} SQL.
    {% if sql_flavor == 'bigquery' %}

    BigQuery SQL uses Postgres-flavored syntax, e.g., `EXTRACT(part FROM date_expression)`
    GROUP BY and ORDER BY statements should use numbers instead of column names, e.g., `GROUP BY 1, 2`

    {% endif %}
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
    Write the SQL that answers the following question:

    """{{user_query}}"""
    {% if prompt_addendum %}

    {{prompt_addendum}}

    {% endif %}
    Task: Respond with only one concise SQL statement.
    ''')

finetuned_prompt_template = jinja2.Template('''Schema: {{schema}}\nQuestion: {{user_query}}\n\n###\n\n''')

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


def assemble_prompt(user_query: str, schema: str, descriptions: Optional[List[str]]=None, sql_flavor=None, prompt_addendum: Optional[str]=None) -> str:
    return prompt_template.render(
        user_query=user_query,
        schema=schema,
        descriptions=descriptions,
        sql_flavor=sql_flavor,
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
