"""Test PATCH /geofencer/shapes/{shape_id}."""
from fastapi.testclient import TestClient

from .conftest import ExampleDbAbc


def test_delete(client: TestClient, db: ExampleDbAbc) -> None:
    """This should only delete the shapes in the organization."""
    shape_ids = [
        str(db.shapes[shp].uuid)
        for shp in (
            "pink-objective",
            "convoluted-sledder",
            "isobaric-concentration",
            "short-bulldozer",
            "several-sword",  # not in the org
        )
    ]
    response = client.delete("/geofencer/shapes", params={"shape_ids": shape_ids})  # type: ignore
    assert response.status_code == 200
    expected_deleted = {
        str(db.shapes[shp].uuid)
        for shp in (
            "pink-objective",
            "convoluted-sledder",
            "isobaric-concentration",
            "short-bulldozer",
        )
    }
    # delete succeeds but the deleted ids are not included in this
    assert set(response.json()["deleted_ids"]) == set(expected_deleted)
