import os
import re

from fastapi import FastAPI
import openai
from pydantic import BaseModel
import sqlparse

openai.api_key = os.environ['OPENAI_KEY']

app = FastAPI()

@app.get("/")
def read_root():
    return "Have no sphere - Copyright Mercator 2023"


# Regex that matches a SQL table schema
# Allow quoted table names and column names
SQL_TABLE_REGEX = r"""
    ^CREATE\s+TABLE.*\(
"""

# Createa Pydanic model for the response
class QueryResponse(BaseModel):
    query_text: str


@app.get("/v1/dubo/query", 
    response_model=QueryResponse,
    responses={
        422: {"description": "Invalid schema"},
        429: {"description": "Too many requests"},
        500: {"description": "No suitable response for the given query."},
        503: {"description": "Service unavailable"}
    }
)
def read_query(
    schema: str,
    query: str
):
    parsed = sqlparse.parse(schema)[0]
    # Really rough check to make sure the input is a valid SQL table schema
    assert parsed.tokens[0].value.upper() == "CREATE", "Invalid schema"
    prompt = f'''
    Convert text to SQL.
    
    You have a table of input with the following schema:
    
    {schema}
    
    Write the SQL that answers the following question:
    
    """{query}"""
    
    Be specific.
    '''

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    if response.choices:  # type: ignore
        return {
            "query_text": response.choices[0].text.strip() # type: ignore
        }
    else:
        raise Exception("No suitable response for the given query.")