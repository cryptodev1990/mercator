from typing import List
import os

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
import openai
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import sqlparse

from api.gateways.conns import run_query_against_connection
from api.gateways.openai import assemble_prompt, get_sql_from_gpt_prompt
from api.schemas.responses import QueryResponse, ResultsResponse

openai.api_key = os.environ['OPENAI_KEY']

app = FastAPI()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/")
def read_root():
    return "Have no sphere - Copyright Mercator 2023"


# Regex that matches a SQL table schema
# Allow quoted table names and column names
SQL_TABLE_REGEX = r"""
    ^CREATE\s+TABLE.*\(
"""

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
@limiter.limit("100/day")
def read_query(
    request: Request,
    user_query: str = Query(default=None, description="The question to answer"),
    schemas: List[str] = Query(default=[], description="The table schema(s) to use"),
    descriptions: List[str] | None = Query(default=[], description="The table description(s) to use")
):
    if not user_query:
        raise HTTPException(status_code=422, detail="No query provided")
    if not schemas:
        raise HTTPException(status_code=422, detail="No schemas provided")

    try:
        parsed = sqlparse.parse(schemas[0])[0]
        # Really rough check to make sure the input is a valid SQL table schema
        assert parsed.tokens[0].value.upper() == "CREATE", "Invalid schema"
        for s_to_check in [user_query, *schemas, *descriptions]:  # type: ignore
            if not s_to_check:
                continue
            assert '```' not in s_to_check, "Reserved tokens in query"
            assert '"""' not in s_to_check, "Reserved tokens in query"
    except AssertionError as e:
        raise HTTPException(status_code=422, detail=str(e))

    schema = '\n'.join(schemas)
    print(schema)
    prompt = assemble_prompt(user_query, schema, descriptions)
    print(prompt)

    sql = get_sql_from_gpt_prompt(prompt)
    if sql:
        return QueryResponse(query_text=sql)
    raise HTTPException(status_code=400, detail="No suitable response for the given query.")


@app.get("/v1/dubo/query/{conn_id}",
    response_model=ResultsResponse,
    responses={
        422: {"description": "Invalid schema"},
        429: {"description": "Too many requests"},
        500: {"description": "No suitable response for the given query."},
        503: {"description": "Service unavailable"}
    },
    tags=["dubo"],
    summary="Convert text to SQL for a specific connection",
)
@limiter.limit("100/day")
def read_query_conn(
    conn_id: str,
    request: Request,
    user_query: str = Query(default=None, description="The question to answer"),
):
    if not user_query:
        raise HTTPException(status_code=422, detail="No query provided")

    resp = run_query_against_connection(conn_id, user_query)
    if resp:
        return resp
    raise HTTPException(status_code=400, detail="No suitable response for the given query.")