from typing import List
from fastapi import APIRouter, HTTPException, Query, Request
import sqlparse
from api.schemas.responses import QueryResponse, ResultsResponse
from api.rate_limiter import is_request_exempt, limiter

from api.gateways.openai import assemble_prompt, assemble_finetuned_prompt, get_sql_from_gpt_prompt, get_sql_from_gpt_finetuned
from api.gateways.conns import run_query_against_connection


router = APIRouter()


@router.get("/dubo/query",
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
@limiter.limit("100/day", exempt_when=is_request_exempt)
def read_query(
    request: Request,
    user_query: str = Query(default=None, description="The question to answer"),
    schemas: List[str] = Query(default=[], description="The table schema(s) to use"),
    descriptions: List[str] | None = Query(default=[], description="The table description(s) to use"),
    finetuned: bool = Query(default=False, description="Whether to use the finetuned model")
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
    if not finetuned: 
        prompt = assemble_prompt(user_query, schema, descriptions)
        sql = get_sql_from_gpt_prompt(prompt)
    else: 
        prompt = assemble_finetuned_prompt(user_query, schema)
        sql = get_sql_from_gpt_finetuned(prompt)

    print(prompt)
    print(sql)
    
    if sql:
        return QueryResponse(query_text=sql)
    raise HTTPException(status_code=400, detail="No suitable response for the given query.")


@router.get("/dubo/query/{conn_id}",
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
@limiter.limit("100/day", exempt_when=is_request_exempt)
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
