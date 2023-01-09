from typing import List, Optional
import os

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
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


origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/v1/dubo/query",
    response_model=QueryResponse,
    responses={
        422: {"description": "Invalid schema"},
        429: {"description": "Too many requests"},
        500: {"description": "No suitable response for the given query."},
        503: {"description": "Service unavailable"}
    },
    tags=["dubo"],
    summary="Convert text to SQL",
)
def read_query(
    user_query: str = Query(default=None, description="The question to answer"),
    schemas: List[str] = Query(default=[], description="The table schema(s) to use"),
    descriptions: List[str] | None = Query(default=[], description="The table description(s) to use")
): 
    if not user_query:
        raise HTTPException(status_code=422, detail="No query provided")
    if not schemas:
        raise HTTPException(status_code=422, detail="No schemas provided")
    try:
        descriptions = descriptions or []
        parsed = sqlparse.parse(schemas[0])[0]
        # Really rough check to make sure the input is a valid SQL table schema
        assert parsed.tokens[0].value.upper() == "CREATE", "Invalid schema"
        for s_to_check in [user_query, *schemas, *descriptions]:
            if not s_to_check:
                continue
            assert '```' not in s_to_check, "Reserved tokens in query"
            assert '"""' not in s_to_check, "Reserved tokens in query"
    except AssertionError as e:
        raise HTTPException(status_code=422, detail=str(e))

    schema = '\n'.join(schemas)

    print(schema)

    prompt = f'''
    Convert text to SQL.

    You have the following DDLs:

    ```
    {schema}
    ```

    Write the SQL that answers the following question:

    """{user_query}"""

    Respond with only one concise SQL statement.
    '''

    print(prompt)

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    if response.choices:  # type: ignore
        return {
            "query_text": response.choices[0].text.strip() # type: ignore
        }
    raise HTTPException(status_code=400, detail="No suitable response for the given query.")
