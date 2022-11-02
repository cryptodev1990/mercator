"""Test DELETE /geofencer/shapes/{shape_id}."""
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.crud.shape import shape_exists

from .conftest import ExampleDbAbc


def test_shape_self(client: TestClient, db: ExampleDbAbc) -> None:
    shape_id = db.shapes["pink-objective"].uuid
    response = client.delete(f"/geofencer/shapes/{shape_id}")
    assert response.status_code == 204
    assert not shape_exists(db.conn, shape_id)
    assert shape_exists(db.conn, shape_id, include_deleted=True)


def test_shape_not_exists(client: TestClient, db: ExampleDbAbc) -> None:
    shape_ids = set(db.conn.execute(text("SELECT uuid from shapes")).scalars())
    while (shape_id_not_exists := uuid.uuid4()) in shape_ids:
        pass
    response = client.delete(f"/geofencer/shapes/{shape_id_not_exists}")
    assert response.status_code == 404


def test_same_org(client: TestClient, db: ExampleDbAbc) -> None:
    shape_id = db.shapes["short-bulldozer"].uuid
    response = client.delete(f"/geofencer/shapes/{shape_id}")
    assert response.status_code == 204
    assert not shape_exists(db.conn, shape_id)
    assert shape_exists(db.conn, shape_id, include_deleted=True)


def test_diff_org(client: TestClient, db: ExampleDbAbc) -> None:
    shape_id = db.shapes["several-sword"].uuid
    response = client.delete(f"/geofencer/shapes/{shape_id}")
    assert response.status_code == 404
