import os
from typing import List
import jinja2

import openai

openai.api_key = os.environ['OPENAI_KEY']

prompt_template = jinja2.Template('''
    Convert text to {{sql_flavor or 'ANSI'}} SQL.

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

    Respond with only one concise SQL statement.
    ''')

finetuned_prompt_template = jinja2.Template('''Schema: {{schema}}\nQuestion: {{user_query}}\n\n###\n\n''')

def get_sql_from_gpt_prompt(prompt: str) -> str | None:
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


def assemble_prompt(user_query: str, schema: str, descriptions: List[str] | None=None, sql_flavor=None) -> str:
    return prompt_template.render(
        user_query=user_query,
        schema=schema,
        descriptions=descriptions,
        sql_flavor=sql_flavor
    )

finetuned_engine = "davinci:ft-mercator-2023-01-25-23-01-53"

def get_sql_from_gpt_finetuned(prompt: str) -> str | None:
    completions = openai.Completion.create(
             engine=finetuned_engine,
             prompt=prompt,
             max_tokens=1024,
             n=1,
             stop=["\n"],
             temperature=0.5
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