import base64
import json
import os
from requests import head
import sqlglot
import yaml

from typing import Optional, Union, List

from google.cloud import bigquery
from api.core.logging import get_logger
from fastapi import HTTPException

from api.gateways.openai import assemble_finetuned_prompt, assemble_prompt, get_sql_from_gpt_prompt
from api.handlers.handler_utils import sql_response_headers
from api.handlers.sql_utils.query_cleaning import QueryCleaner
from api.schemas.responses import ResultsResponse

here = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(here, '../connections.yaml'), 'r') as f:
    config = yaml.safe_load(f)


logger = get_logger(__name__)


memoized_connections = {}


def base64_to_dict(b64: str) -> dict:
    decoded = base64.b64decode(b64).decode('utf-8')
    return json.loads(decoded, strict=False)


google_creds = base64_to_dict(
    os.environ['GOOGLE_APPLICATION_CREDENTIALS_JSON'])


class Connection:
    def __init__(self, conn_id, **kwargs):
        self.conn_id = conn_id
        self.connection_type = kwargs['connection_type']
        self.ddl = kwargs.get('ddl')
        if self.ddl:
            self.ddl = clean_ddls(self.ddl, sql_flavor=self.connection_type)
        self.prompt_addendum = kwargs.get('prompt_addendum')
        self.kwargs = kwargs
        # BigQuery client, if needed
        self._client = None

    def execute(self, query: str):
        """Execute a query against the connection"""
        if self.connection_type == 'bigquery':
            if not self._client:
                self._client = bigquery.Client.from_service_account_info(
                    google_creds)
            qj = self._client.query(query)
            # Get results from query job
            return [x for x in qj.result()]
        raise TypeError(f"Invalid connection type: {self.connection_type}")

    @staticmethod
    def make_conn(conn_id: str):
        if memoized_connections.get(conn_id):
            return memoized_connections[conn_id]
        conn = Connection(conn_id, **config[conn_id])
        memoized_connections[conn_id] = conn
        return conn

    def make_prompt(self, query: str, ddl_line_filter: Optional[List[str]] = None, finetune: bool = False) -> str:
        """Make the prompt for the API"""
        if not self.ddl:
            raise Exception("Prompt requires DDL")
        ddls = [self.ddl]
        if ddl_line_filter is not None:
            # Filter out lines that don't match the filter by a match to ddl_line_filter
            # Kind of a hack
            ddls = []
            for filtered in ddl_line_filter:
                for potential_ddl in self.ddl.splitlines():
                    if filtered in potential_ddl:
                        ddls.append(potential_ddl)
        ddls = '\n'.join(ddls)
        if finetune:
            prompt = assemble_finetuned_prompt(query, ddls)
            return prompt
        prompt = assemble_prompt(
            query, ddls, prompt_addendum=self.prompt_addendum)
        return prompt


def run_query_against_connection(conn_id: str, user_query: str) -> ResultsResponse:
    """Run a query against a connection"""
    if conn_id not in config:
        raise HTTPException(status_code=422, detail="Invalid connection ID")
    conn = Connection.make_conn(conn_id)
    prompt = conn.make_prompt(user_query)
    logger.info({
        "event": "query",
        "conn_id": conn_id,
        "user_query": user_query,
        "prompt": prompt
    })
    sql = get_sql_from_gpt_prompt(prompt)
    if not sql:
        raise HTTPException(
            status_code=400, detail="No suitable response for the given query.")

    # Transformation pipeline
    qc = QueryCleaner(sql, sql_flavor=conn.connection_type).add_limit(
    ).guard_against_divide_by_zero()
    if not qc.is_select_statement():
        raise HTTPException(
            status_code=400, detail="Your query generated a non-SELECT SQL statement. Only SELECT statements are allowed. Please try again.")

    logger.info({
        "event": "sql",
        "conn_id": conn_id,
        "user_query": user_query,
        "sql": sql,
        "cleaned_sql": qc.text()
    })
    try:
        results = conn.execute(sql)
    except Exception as e:
        headers = sql_response_headers(sql)
        raise HTTPException(
            status_code=400, detail=f"Error executing query: {e}", headers=headers)
    results: list[dict[str, Optional[Union[str, float, int, bool]]]] = [
        dict(x) for x in results]
    return ResultsResponse(query_text=sql, results=results)  # type: ignore


def clean_ddls(ddl: str, sql_flavor='sqlite') -> str:
    """Make the DDLs clean for the prompt"""
    parsed = sqlglot.parse(ddl, read=sql_flavor)
    if parsed is None:
        raise Exception("Invalid DDL")
    new_ddls = []
    for x in parsed:
        if x is None:
            raise Exception("Invalid DDL")
        new_ddls.append(x.sql(dialect=sql_flavor, indent=0))
    return '\n'.join(new_ddls)
