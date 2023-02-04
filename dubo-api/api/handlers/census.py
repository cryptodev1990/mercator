# https://api.census.gov/data/2021/acs/acs5?get=NAME,B01001_001E&for=zip%20code%20tabulation%20area:*
# https://api.census.gov/data/2021/acs/acs5/variables.html
"""
This is a ruckus mad-dash demo endpoint for the census API.
"""
from typing import List, Optional, Union
from io import BytesIO
import os
import re
import time

import asyncpg
import openai
import pandas as pd
from pydantic import NonNegativeInt
import sqlglot

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse

from api.gateways.conns import Connection
from api.gateways.openai import get_sql_from_gpt_finetuned, get_sql_from_gpt_prompt
from api.handlers.sql_utils import guard_against_divide_by_zero, grab_from_select_onwards
from api.handlers.autocomplete import get_autocomplete


openai.api_key = os.environ['OPENAI_KEY']
BUCKET = 'dubo-api-storage'
ONE_HUNDRED_RE = r'\s?[*]\s?100(.0)?'


# Create an async postgres connection
async def connect_to_db():
    try:
        # TODO we need to make this a pool
        return await asyncpg.connect(os.environ['CENSUS_DATABASE_URL'])
    except Exception as e:
        print({
            "event": "error",
            "error": "error connecting to database",
        })
        print(e)
        return None


async def check_cache(query: str, conn: asyncpg.Connection) -> str:
    # We have an UNLOGGED table that stores the results of queries
    # CREATE UNLOGGED TABLE census_queries (query TEXT, approved_sql TEXT);
    # CREATE INDEX ON census_queries (query);
    # ALTER TABLE census_queries ADD COLUMN id SERIAL PRIMARY KEY;
    res = await conn.fetch(
        'SELECT approved_sql FROM census_queries WHERE query = $1', query.lower())
    if len(res) > 0:
        return res[0][0]
    return None


router = APIRouter(
    tags=['census'],
)


zcta_prompt_factory = Connection.make_conn("acs-zctas")


@router.get("/db-health")
async def db_health(conn=Depends(connect_to_db)):
    if conn is None:
        raise NotImplementedError('Database connection not implemented')
    return await conn.fetch('SELECT 1')


# make the route send octet-stream
@router.get('/census', response_class=StreamingResponse)
async def census(
    query: str,
    request: Request,
    conn=Depends(connect_to_db),
):
    ip = request.client.host
    if conn is None:
        raise NotImplementedError('Database connection not implemented')

    # Check the cache
    cached_sql = await check_cache(query, conn)
    if cached_sql is not None:
        sql = cached_sql
        print({
            "event": "cache_hit",
            "ip": ip,
            "sql": sql,
            "query": query,
        })
    else:
        sql = await _get_census_sql_from_query(query, conn, ip)
    start = time.time()
    records = await conn.fetch(sql)
    print({
        "event": "fetched_records",
        "records": len(records),
        "seconds": time.time() - start,
        "ip": ip,
    })
    if len(records) == 0:
        raise HTTPException(status_code=404, detail="No results found")
    df = pd.DataFrame(records, columns=records[0].keys())
    print(df.head())
    parquet = df.dropna().to_parquet(index=False)
    return StreamingResponse(BytesIO(parquet), media_type="application/octet-stream", headers={
        # "X-Generated-Sql": sql,
    })


@router.post('/feedback/census')
async def feedback_census(
    q: str,
    sql: str,
    conn=Depends(connect_to_db),
):
    if conn is None:
        raise NotImplementedError('Database connection not implemented')
    try:
        sql = sqlglot.transpile(sql, read='postgres',
                                write='postgres', pretty=True)[0]
    except Exception as e:
        return HTTPException(status_code=400, detail="Invalid SQL")
    await conn.execute(
        'INSERT INTO census_queries (query, approved_sql) VALUES ($1, $2)', q.lower(), sql)
    return {'status': 'ok'}


def cleaning_pipeline(input_sql: str) -> str:
    sql = grab_from_select_onwards(' '.join(input_sql.split('\n')))
    try:
        sql = sqlglot.transpile(
            sql, read='sqlite', write='postgres', pretty=False)[0]
        # For whatever reason gpt-3 loves multiplying percentages by 100 or 100.0
        if re.match(ONE_HUNDRED_RE, sql):
            sql = re.sub(ONE_HUNDRED_RE, '', sql)
        # GPT-3 also loves to divide by 0
        sql = guard_against_divide_by_zero(sql)
    except Exception as e:
        print("cleaning pipeline failed, defaulting to original sql")
        print(e)
    return input_sql


TABLES = [
    "acs_sex_by_age",
    "acs_race",
    "acs_hispanic",
    "acs_commute_times",
    "acs_employment_by_industry",
    "acs_commute_modes",
    "acs_education_subjects",
    "acs_housing_year_built",
    "acs_poverty_status",
    "acs_ratio_of_income_to_poverty_level",
    "acs_earners_in_household",
    "acs_housing",
    "acs_medicare",
    "acs_gross_rent_household_income_ratio",
]


async def _get_census_sql_from_query(query: str, conn: asyncpg.Connection, ip: str) -> str:
    NEWLINE = '\n'

    prompt_1 = f"""
        You are a data scientist. You have the following SQL tables of US Census data to choose from:

        {NEWLINE.join(TABLES)}

        Which table would best answering the question ```{query}```? Respond with only the table name.
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt_1,
        temperature=0.9,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    table = response.choices[0].text.strip()  # type: ignore
    try:
        assert table in TABLES, f'Invalid table: {table}'
    except AssertionError as e:
        print({
            "event": "error",
            "error": "invalid table",
            "table": table,
            "ip": ip,
        })
        raise HTTPException(
            status_code=404, detail="Query does not relate to a known data source")

    prompt_2 = zcta_prompt_factory.make_prompt(
        query, ddl_line_filter=table, finetune=False)
    start = time.time()
    sql = get_sql_from_gpt_prompt(prompt_2)
    if sql is None:
        raise HTTPException(status_code=404, detail="No results found")
    print({
        "event": "sql",
        "sql": sql,
        "prompt": prompt_2,
        "seconds": time.time() - start,
        "ip": ip,
    })
    print('======')
    print(query)
    print(sql)
    print('======')
    sql = cleaning_pipeline(sql)
    print({
        "event": "cleaned_sql",
        "sql": sql,
        "ip": ip,
    })
    return sql


_autocomplete = get_autocomplete()
QUERY_MAX_SIZE = 5


@router.get(
    "/census/autocomplete",
    response_model=List[str],
    responses={"400": {"description": "Unable to parse query."}},
)
async def _autocomplete_endpoint(
    text: str = Query(..., example="Where is",
                      description="Incomplete text."),
    limit: NonNegativeInt = Query(
        QUERY_MAX_SIZE, description="Maximum number of results to return"),
) -> List[str]:
    """Autocomplete endpoint for text search queries"""

    size = limit if limit <= QUERY_MAX_SIZE else QUERY_MAX_SIZE
    results = _autocomplete.search(text, max_cost=1000, size=size)

    return [j for i in results for j in i]
