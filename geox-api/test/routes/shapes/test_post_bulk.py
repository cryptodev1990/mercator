"""Test POST /geofencer/shapes/bulk"""
from typing import Any, Dict, List

import pytest
from fastapi.testclient import TestClient

from .conftest import ExampleDbAbc

_new_geom = {
    "coordinates": [[[8, -57], [62, 10], [-1, 7], [-88, -27], [8, -57]]],
    "type": "Polygon",
}
_new_name = "bright-curve"
_new_props = {"foo": "bar"}


@pytest.fixture()
def examples(db: ExampleDbAbc) -> List[Dict[str, Any]]:
    default_namespace_id = str(db["example.com"].default_namespace.id)
    new_namespace_id = str(db["example.com"].namespaces["new-namespace"].id)

    EXAMPLES: Dict[str, Dict[str, Any]] = {
        "geojson only": {
            "data": {
                "geojson": {
                    "type": "Feature",
                    "geometry": _new_geom,
                    "properties": {"name": _new_name, **_new_props},
                }
            },
            "expected": {
                "geojson": {
                    "type": "Feature",
                    "geometry": _new_geom,
                    "properties": {"name": _new_name, **_new_props},
                },
                "namespace_id": default_namespace_id,
            },
        },
        "geojson with name": {
            "data": {
                "name": _new_name,
                "geojson": {
                    "type": "Feature",
                    "geometry": _new_geom,
                    "properties": {"name": "bad name", **_new_props},
                },
            },
            "expected": {
                "geojson": {
                    "type": "Feature",
                    "geometry": _new_geom,
                    "properties": {"name": _new_name, **_new_props},
                },
                "namespace_id": default_namespace_id,
            },
        },
        "no name or props": {
            "data": {
                "geojson": {
                    "type": "Feature",
                    "geometry": _new_geom,
                    "properties": {},
                },
            },
            "expected": {
                "geojson": {
                    "type": "Feature",
                    "geometry": _new_geom,
                    "properties": {},
                },
                "namespace_id": default_namespace_id,
            },
        },
        "with namespace": {
            "data": {
                "geojson": {
                    "type": "Feature",
                    "geometry": _new_geom,
                    "properties": {},
                },
                "namespace": new_namespace_id,
            },
            "expected": {
                "geojson": {
                    "type": "Feature",
                    "geometry": _new_geom,
                    "properties": {},
                },
                "namespace_id": new_namespace_id,
            },
        },
        "geometry, properties, name": {
            "data": {
                "geometry": _new_geom,
                "name": _new_name,
                "properties": {"name": "bad name"},
            },
            "expected": {
                "geojson": {
                    "type": "Feature",
                    "geometry": _new_geom,
                    "properties": {"name": _new_name},
                },
                "namespace_id": default_namespace_id,
            },
        },
        "geometry, properties with NAME": {
            "data": {
                "geometry": _new_geom,
                "properties": {"NAME": _new_name},
            },
            "expected": {
                "geojson": {
                    "type": "Feature",
                    "geometry": _new_geom,
                    "properties": {"name": _new_name},
                },
                "namespace_id": default_namespace_id,
            },
        },
        "geojson.properties with NaMe": {
            "data": {
                "geojson": {
                    "type": "Feature",
                    "geometry": _new_geom,
                    "properties": {"NAME": _new_name},
                }
            },
            "expected": {
                "geojson": {
                    "type": "Feature",
                    "geometry": _new_geom,
                    "properties": {"name": _new_name},
                },
                "namespace_id": default_namespace_id,
            },
        },
    }
    return [x["data"] for x in EXAMPLES.values()]


# pylint: disable=unused-argument, redefined-outer-name
def test_post(
    client: TestClient, db: ExampleDbAbc, examples: List[Dict[str, Any]]
) -> None:
    n_shapes = len(examples)
    response = client.post("/geofencer/shapes/bulk", json=examples)
    assert response.status_code == 200
    actual = response.json()
    assert actual["num_shapes"] == n_shapes


# pylint: enable=unused-argument, redefined-outer-name
