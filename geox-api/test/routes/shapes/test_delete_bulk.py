"""Test DELETE /geofencer/shapes/bulk."""
import json

from fastapi.testclient import TestClient

from .conftest import ExampleDbAbc


def test_delete_bulk(client: TestClient, db: ExampleDbAbc) -> None:
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
    response = client.delete("/geofencer/shapes/bulk", json=shape_ids)  # type: ignore
    assert response.status_code == 200
    expected = {"num_shapes": 4}
    # delete succeeds but the deleted ids are not included in this
    assert response.json() == expected
