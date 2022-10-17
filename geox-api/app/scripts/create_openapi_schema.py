"""Post-processes openapi.json

This script post-processes the openapi.json to produce valid typescript models
using `opeanpi-typescript-codegen`.
"""

import json

import typer

from app.main import app


def fix_bbox(schema):
    bbox = schema["components"]["schemas"]["Feature"]["properties"]["bbox"]
    del bbox["anyOf"]
    bbox["type"] = "array"
    bbox["items"] = {"type": "number"}
    return schema


def fix_point(schema):
    coord = schema["components"]["schemas"]["Point"]["properties"]["coordinates"]
    coord["type"] = "array"
    del coord["anyOf"]
    coord["maxItems"] = 3
    coord["minItems"] = 2
    coord["items"] = {"type": "number"}
    return schema


def fix_polygon(schema):
    coord = schema["components"]["schemas"]["Polygon"]["properties"]["coordinates"]
    coord["type"] = "array"
    coord["items"] = {"type": "array", "items": {"type": "number"}}
    return schema


def fix_line_string(schema):
    coord = schema["components"]["schemas"]["LineString"]["properties"]["coordinates"]
    coord["type"] = "array"
    coord["maxItems"] = 3
    coord["minItems"] = 2
    coord["items"] = {"type": "number"}
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
    coord = schema["components"]["schemas"]["MultiLineString"]["properties"][
        "coordinates"
    ]
    # Each item is a line-string
    coord["items"] = {
        "type": "array",
        # each item is a point (2-3 numbers)
        "items": {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 2,
            "maxItems": 3,
        },
    }
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
    coord = schema["components"]["schemas"]["MultiPoint"]["properties"]["coordinates"]
    coord["type"] = "array"
    coord["items"] = {
        "type": "array",
        "minItems": 2,
        "maxItems": 3,
        "items": {"type": "number"},
    }
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
    coord = schema["components"]["schemas"]["MultiPolygon"]["properties"]["coordinates"]
    # outer array = list of polygons
    coord["type"] = "array"
    coord["items"] = {
        # polygon is a list of coordinates
        "type": "array",
        "items": {
            # each point is 2-3 numbers
            "type": "array",
            "minItems": 2,
            "maxItems": 3,
            "items": {"type": "number"},
        },
    }
    return schema


from pathlib import Path
from typing import Optional

import typer


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
    schema_str = json.dumps(schema, indent=2)
    if output:
        with output.open("w") as f:
            f.write(schema_str)
    else:
        typer.echo(schema_str)


if __name__ == "__main__":
    typer.run(main)
