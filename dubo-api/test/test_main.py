import sqlite3
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
    response = client.get("/v1/dubo/query", params={"schemas": ["create TABLE tbl (bar INT);"], "user_query": "What are the total values in bar?"})
    assert response.status_code == 200
    assert response.json()["query_text"] == "SELECT SUM(bar) FROM tbl;"


def test_read_query_with_dubo():
    response = client.get("/v1/dubo/query?user_query=What%20are%20the%20coolest%20bars%20in%20Des%20Moines%3F&schemas=CREATE%20TABLE%20bars%20%28id%20INTEGER%2C%20coolest%20BOOLEAN%29%3B&schemas=CREATE%20TABLE%20des_moines_bars%20%28id%20INTEGER%29%3B")
    assert response.status_code == 200
    query = response.json()["query_text"].replace('\n', ' ')

    # Create an in-memory SQLite database
    conn = sqlite3.connect(":memory:")
    c = conn.cursor()

    # Create the tables
    c.execute("CREATE TABLE bars (id INTEGER, coolest BOOLEAN);")
    c.execute("CREATE TABLE des_moines_bars (id INTEGER);")

    # Insert some data
    c.execute("INSERT INTO bars VALUES (1, True);")
    c.execute("INSERT INTO bars VALUES (2, False);")
    c.execute("INSERT INTO des_moines_bars VALUES (1);")

    # Execute the query
    c.execute(query)

    # Check the results
    assert c.fetchall() == [(1,)]