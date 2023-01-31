# https://api.census.gov/data/2021/acs/acs5?get=NAME,B01001_001E&for=zip%20code%20tabulation%20area:*
# https://api.census.gov/data/2021/acs/acs5/variables.html
"""
This is a ruckus mad-dash demo endpoint for the census API.
"""
from io import BytesIO
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

import pandas as pd
import openai
import asyncpg

from api.core.logging import get_logger

from api.gateways.conns import Connection

openai.api_key = os.environ['OPENAI_KEY']
BUCKET = 'dubo-api-storage'

logger = get_logger(__name__)


# Create an async postgres connection
async def connect_to_db():
    try:
        return await asyncpg.connect(os.environ['CENSUS_DATABASE_URL'])
    except Exception as e:
        print("Error connecting to database")
        print(e)
        return None


router = APIRouter(
    tags=['census'],
)


zcta_prompt_factory = Connection.make_conn("acs-zctas")


@router.get("/db-health")
async def db_health(conn = Depends(connect_to_db)):
    if conn is None:
        raise NotImplementedError('Database connection not implemented')
    return await conn.fetch('SELECT 1')


# make the route send octet-stream
@router.get('/census', response_class=StreamingResponse)
async def census(
   query: str,
   conn = Depends(connect_to_db)
):
    if conn is None:
        raise NotImplementedError('Database connection not implemented')

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
    assert table in TABLES, f'Invalid table: {table}'

    prompt_2 = zcta_prompt_factory.make_prompt(query, ddl_line_filter=table)

    print(prompt_2)

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt_2,
        temperature=0.9,
        max_tokens=2000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    sql = response.choices[0].text  # type: ignore
    print(sql)
    records = await conn.fetch(sql)
    if len(records) == 0:
        raise HTTPException(status_code=404, detail="No results found")
    df = pd.DataFrame(records, columns=records[0].keys())
    print(df.head())
    parquet = df.dropna().to_parquet(index=False)
    return StreamingResponse(BytesIO(parquet), media_type="application/octet-stream")