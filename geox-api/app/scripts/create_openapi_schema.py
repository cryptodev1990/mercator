"""Post-processes openapi.json

This script post-processes the openapi.json to produce valid typescript models
using `opeanpi-typescript-codegen`.
"""

import json
from pathlib import Path
from typing import Optional

import typer

from app.main import app


def fix_bbox(schema):
    bbox = {"type": "array", "items": {"type": "number"}}
    schema["components"]["schemas"]["Feature"]["properties"]["bbox"] = bbox
    return schema


def fix_point(schema):
    coord = {"type": "array", "items": {"type": "number"}}
    schema["components"]["schemas"]["Point"]["properties"]["coordinates"] = coord
    return schema


def fix_polygon(schema):
    coord = {"type": "array", "items": {"type": "array", "items": {"type": "number"}}}
    schema["components"]["schemas"]["Polygon"]["properties"]["coordinates"] = coord
    return schema


def fix_line_string(schema):
    coord = {"type": "array", "items": {"type": "array", "items": {"type": "number"}}}
    schema["components"]["schemas"]["LineString"]["properties"]["coordinates"] = coord
    return schema


def fix_multi_line_string(schema):
    # Desired: Array<Array<Array<number>>>
    #    {
    #    "type": "MultiLineString",
    #    "coordinates": [
    #      [
    #        [100.0, 0.0],
    #        [101.0, 1.0]
    #      ],
    #      [
    #        [102.0, 2.0],
    #        [103.0, 3.0]
    #      ]
    #    ]
    #  }
    coord = {
        "type": "array",
        "items": {
            "type": "array",
            # each item is a point (2-3 numbers)
            "items": {
                "type": "array",
                "items": {"type": "number"},
                "minItems": 2,
                "maxItems": 3,
            },
        },
    }
    schema["components"]["schemas"]["MultiLineString"]["properties"][
        "coordinates"
    ] = coord
    # Each item is a line-string
    return schema


def fix_multi_point(schema):
    # Original output:     coordinates: Array<>;
    # Desired: coordinates: Array<Array<number>>
    # Example:
    #  {
    #    "TYPE": "MultiPoint",
    #    "coordinates": [
    #      [100.0, 0.0],
    #      [101.0, 1.0]
    #    ]
    #  }
    coord = {
        "type": "array",
        "items": {
            "type": "array",
            "minItems": 2,
            "maxItems": 3,
            "items": {"type": "number"},
        },
    }
    schema["components"]["schemas"]["MultiPoint"]["properties"]["coordinates"] = coord
    return schema


def fix_multi_polygon(schema):
    # Orig output:
    # Desired: Array<Array<Array<number>>>
    # Example:
    #     {
    # "type": "MultiPolygon",
    # "coordinates": [
    #     [
    #     [
    #         [102.0, 2.0],
    #         [103.0, 2.0],
    #         [103.0, 3.0],
    #         [102.0, 3.0],
    #         [102.0, 2.0]
    #     ]
    #     ],
    #     [
    #     [
    #         [100.0, 0.0],
    #         [101.0, 0.0],
    #         [101.0, 1.0],
    #         [100.0, 1.0],
    #         [100.0, 0.0]
    #     ],
    #     [
    #         [100.2, 0.2],
    #         [100.2, 0.8],
    #         [100.8, 0.8],
    #         [100.8, 0.2],
    #         [100.2, 0.2]
    #     ]
    #     ]
    # ]
    # }
    # Array<         // list of polygons
    #   Array<       // polygon
    #     Array<   // point - 2-3 numbers

    # outer array = list of polygons
    coord = {
        "items": {
            # polygon is a list of coordinates
            "type": "array",
            "items": {
                # each point is 2-3 numbers
                "type": "array",
                "minItems": 2,
                "maxItems": 3,
                "items": {"type": "number"},
            },
        },
        "type": "array",
    }
    schema["components"]["schemas"]["MultiPolygon"]["properties"]["coordinates"] = coord
    return schema


def fix_bbox_params(schema):
    # Fix bbox params in some routes
    # Original schema:
    #       "items": [
    #     {
    #       "maximum": 180.0,
    #       "minimum": -180.0,
    #       "type": "number"
    #     },
    #     {
    #       "maximum": 90.0,
    #       "minimum": -90.0,
    #       "type": "number"
    #     },
    #     {
    #       "maximum": 180.0,
    #       "minimum": -180.0,
    #       "type": "number"
    #     },
    #     {
    #       "maximum": 90.0,
    #       "minimum": -90.0,
    #       "type": "number"
    #     }
    #   ]
    # Generated typescript
    # Array<any>
    # Desired typescript
    # Array<number>
    routes = [("/geofencer/shapes", "get"), ("/geofencer/shape-metadata", "get")]
    for path, http_verb in routes:
        params = schema["paths"][path][http_verb]["parameters"]
        for p in params:
            if p["name"] == "bbox":
                p["schema"]["items"] = {"type": "number"}
    return schema


def main(output: Optional[Path] = typer.Option(None, exists=False)) -> None:
    """Generate an openapi schema to use in generating typescript clients."""
    schema = app.openapi()
    schema = fix_bbox(schema)
    schema = fix_point(schema)
    schema = fix_polygon(schema)
    schema = fix_line_string(schema)
    schema = fix_multi_line_string(schema)
    schema = fix_multi_polygon(schema)
    schema = fix_multi_point(schema)
    schema = fix_bbox_params(schema)
    schema_str = json.dumps(schema, indent=2)
    if output:
        with output.open("w") as f:
            f.write(schema_str)
    else:
        typer.echo(schema_str)


if __name__ == "__main__":
    typer.run(main)
