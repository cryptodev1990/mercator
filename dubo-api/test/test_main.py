import io
import sqlite3
import pandas as pd
from fastapi.testclient import TestClient
import pyarrow as pa
import pyarrow.parquet as pq

from api.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "Have no sphere - Copyright Mercator 2023"


def test_read_query():
    response = client.get("/v1/dubo/query", params={"schemas": [
                          "create TABLE tbl (bar INT);"], "user_query": "What are the total values in bar?"})
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


def test_dubo_post():
    response = client.post("/v1/dubo/query", json={
                           "user_query": "How many bars are there that are the coolest?", "schemas": ["create TABLE tbl (id INTEGER, coolest BOOLEAN);"],
                           "descriptions": ["bar - This is a unique identifier for a bar", "coolest - Indicator for if a bar is cool or not."],
                           "data_header": ["id", "coolest"],
                           "data_sample": [[1, True], [2, False]]
                           })
    if response.status_code != 200:
        print(response.json())

    assert response.status_code == 200
    assert response.json()[
        "query_text"] == "SELECT COUNT(*) FROM tbl WHERE coolest = True;"


def test_read_query_from_connection():
    response = client.get("/v1/dubo/query/polygon-blocks", params={
                          "user_query": "How much USD of WMATIC was exchanged on December 15, 2020? Name the resulting column `transactions`."})
    assert response.status_code == 200
    # Both of these queries are correct
    res = response.json()["results"]
    res = pd.DataFrame(res)['transactions'].tolist()

    assert res == [4, 64, 1861, 85755, 308090, 500179, 419088, 620390]


def test_census_query():
    response = client.get("/demos/census", params={
                          "user_query": "Return each ZIP code in the United States"})
    assert response.status_code == 200
    # get the bytes in the FastAPI response
    bytes = response.content
    # convert the bytes to a pandas dataframe
    reader = pa.BufferReader(bytes)
    table = pq.read_table(reader)
    df = table.to_pandas()  # This results in a pandas.DataFrame
    # get the total population
    assert df.count()[0] == 33774
