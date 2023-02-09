from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, Request
import sqlparse
from api.core.logging import get_logger
from api.schemas.requests import DuboQuery
from api.schemas.responses import QueryResponse, ResultsResponse
from api.rate_limiter import is_request_exempt, limiter

from api.gateways.openai import assemble_prompt, assemble_finetuned_prompt, get_sql_from_gpt_prompt, get_sql_from_gpt_finetuned
from api.gateways.conns import run_query_against_connection


logger = get_logger(__name__)


COMMON_ERRORS: Dict[str | int, Dict[str, str]] = {
    422: {"description": "Invalid schema"},
    429: {"description": "Too many requests"},
    500: {"description": "No suitable response for the given query."},
    503: {"description": "Service unavailable"}
}


def check_for_reserved_tokens(user_query: str, schemas: List[str], descriptions: List[str] | None) -> str:
    parsed = sqlparse.parse(schemas[0])[0]
    # Really rough check to make sure the input is a valid SQL table schema
    assert parsed.tokens[0].value.upper() == "CREATE", "Invalid schema"
    # type: ignore
    for s_to_check in [user_query, *schemas, *(descriptions or [])]:
        if not s_to_check:
            continue
        for tok in ['```', '"""']:
            assert tok not in s_to_check, "Reserved tokens in query"
    return user_query


router = APIRouter()


@router.post("/dubo/query",
             response_model=QueryResponse,
             responses=COMMON_ERRORS,
             )
@limiter.limit("100/day", exempt_when=is_request_exempt)
def read_query_post(
    request: Request,  # required for limiter
    dq: DuboQuery,
):
    # TODO this should be a pydantic model
    if (dq.data_header and not dq.data_sample) or (dq.data_sample and not dq.data_header):
        raise HTTPException(
            status_code=422, detail="Data sample and headers must both be provided")
    if dq.data_header and dq.data_sample:
        if len(dq.data_sample) == 0:
            raise HTTPException(
                status_code=422, detail="Data sample must have at least one row")
        if len(dq.data_header) != len(dq.data_sample[0]):
            raise HTTPException(
                status_code=422, detail="Data sample and headers must be the same length")

    try:
        check_for_reserved_tokens(dq.user_query, dq.schemas, dq.descriptions)
    except AssertionError as e:
        raise HTTPException(status_code=422, detail=str(e))

    schema = '\n'.join(dq.schemas)
    prompt = assemble_prompt(
        dq.user_query,
        schema,
        descriptions=dq.descriptions,
        data_header=dq.data_header,
        data_sample=dq.data_sample)
    sql = get_sql_from_gpt_prompt(prompt)

    logger.info({
        "user_query": dq.user_query,
        "prompt": prompt,
        "sql": sql if sql else "",
    })

    if sql:
        return QueryResponse(query_text=sql)
    raise HTTPException(
        status_code=400, detail="No suitable response for the given query.")


@router.get("/dubo/query",
            response_model=QueryResponse,
            responses=COMMON_ERRORS,
            tags=["dubo"],
            summary="Convert text to SQL",
            )
@limiter.limit("100/day", exempt_when=is_request_exempt)
def read_query(
    request: Request,
    user_query: str = Query(
        default=None, description="The question to answer"),
    schemas: List[str] = Query(
        default=[], description="The table schema(s) to use"),
    descriptions: Optional[List[str]] = Query(
        default=[], description="The table description(s) to use"),
    finetuned: bool = Query(
        default=False, description="Whether to use the finetuned model")
):
    if not user_query:
        raise HTTPException(status_code=422, detail="No query provided")
    if not schemas:
        raise HTTPException(status_code=422, detail="No schemas provided")
    try:
        check_for_reserved_tokens(user_query, schemas, descriptions)
    except AssertionError as e:
        raise HTTPException(status_code=422, detail=str(e))

    schema = '\n'.join(schemas)
    if not finetuned:
        prompt = assemble_prompt(user_query, schema, descriptions)
        sql = get_sql_from_gpt_prompt(prompt)
    else:
        prompt = assemble_finetuned_prompt(user_query, schema)
        sql = get_sql_from_gpt_finetuned(prompt)

    logger.info({
        "user_query": user_query,
        "prompt": prompt,
        "sql": sql if sql else "",
    })

    if sql:
        return QueryResponse(query_text=sql)
    raise HTTPException(
        status_code=400, detail="No suitable response for the given query.")


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
    user_query: str = Query(
        default=None, description="The question to answer"),
):
    if not user_query:
        raise HTTPException(status_code=422, detail="No query provided")

    resp = run_query_against_connection(conn_id, user_query)
    if resp:
        return resp
    raise HTTPException(
        status_code=400, detail="No suitable response for the given query.")
