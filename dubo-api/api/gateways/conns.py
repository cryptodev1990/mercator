import base64
import json
import os
from fastapi import HTTPException
import yaml

from google.cloud import bigquery

from api.gateways.openai import assemble_prompt, get_sql_from_gpt_prompt
from api.schemas.responses import QueryResponse, ResultsResponse

here = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(here, '../connections.yaml'), 'r') as f:
    config = yaml.safe_load(f)


memoized_connections = {}


def base64_to_dict(b64: str) -> dict:
    decoded = base64.b64decode(b64).decode('utf-8')
    return json.loads(decoded, strict=False)


google_creds = base64_to_dict(os.environ['GOOGLE_APPLICATION_CREDENTIALS_JSON'])


class Connection:
    def __init__(self, conn_id, **kwargs):
        self.conn_id = conn_id
        self.connection_type = kwargs['connection_type']
        self.ddl = kwargs.get('ddl')
        self.kwargs = kwargs
        # BigQuery client, if needed
        self._client = None

    def execute(self, query: str):
        """Execute a query against the connection"""
        if self.connection_type == 'bigquery':
            if not self._client:
                self._client = bigquery.Client.from_service_account_info(google_creds)
            qj = self._client.query(query)
            # Get results from query job
            return [x for x in qj.result()]
        raise TypeError(f"Invalid connection type: {self.connection_type}")

    @staticmethod
    def make_conn(conn_id: str):
        if memoized_connections.get(conn_id):
            return memoized_connections[conn_id]
        conn = Connection(conn_id, **config[conn_id])
        print(conn.__dict__)
        memoized_connections[conn_id] = conn
        return conn

    def make_prompt(self, query: str) -> str:
        """Make the prompt for the API"""
        if not self.ddl:
            raise Exception("Prompt requires DDL")
        prompt = assemble_prompt(query, self.ddl, sql_flavor=self.connection_type)
        return prompt


def run_query_against_connection(conn_id: str, user_query: str) -> list[dict]:
    """Run a query against a connection"""
    if conn_id not in config:
        raise HTTPException(status_code=422, detail="Invalid connection ID")
    conn = Connection.make_conn(conn_id)
    prompt = conn.make_prompt(user_query)
    print(prompt)
    sql = get_sql_from_gpt_prompt(prompt)
    if not sql:
        raise HTTPException(status_code=400, detail="No suitable response for the given query.")
    print(sql)
    results = conn.execute(sql)
    results: list[dict[str, str | float | int | bool | None]] = [dict(x) for x in results]
    return ResultsResponse(query_text=sql, results=results) # type: ignore
