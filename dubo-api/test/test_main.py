import pandas as pd
import dubo
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "Have no sphere - Copyright Mercator 2023"


def test_read_query():
    response = client.get("/v1/dubo/query", params={"schema": "create TABLE tbl (bar INT);", "query": "Sum the values in bar"})
    assert response.status_code == 200
    assert response.json()["query_text"] == "SELECT SUM(bar) FROM tbl;"


def test_read_query_with_dubo():
    response = client.get("/v1/dubo/query?query=Sum+the+values+in+bar&schema=CREATE+TABLE+%22tbl%22+%28%0A%22bar%22+INTEGER%0A%29")
    assert response.status_code == 200
    assert response.json()["query_text"] == "SELECT SUM(bar) FROM tbl;"