from pydantic import BaseModel

class QueryResponse(BaseModel):
    query_text: str


class ResultsResponse(QueryResponse):
    results: list