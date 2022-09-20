from fastapi import Response
from typing import Any, Dict, Optional


def tile_to_envelope(x: float, y: float, z: float):
    # Width of world in EPSG:3857
    WORLD_MERC_MAX = 20037508.3427892
    world_merc_min = -1 * WORLD_MERC_MAX
    world_merc_size = WORLD_MERC_MAX - world_merc_min
    # Width in tiles
    world_tile_size = 2**z
    # Tile width in EPSG:3857
    tile_merc_size = world_merc_size / world_tile_size
    # Calculate geographic bounds from tile coordinates
    # XYZ tile coordinates are in "image space" so origin is
    # top-left, not bottom right
    bbox = dict()
    bbox["xmin"] = world_merc_min + tile_merc_size * x
    bbox["xmax"] = world_merc_min + tile_merc_size * (x + 1)
    bbox["ymin"] = WORLD_MERC_MAX - tile_merc_size * (y + 1)
    bbox["ymax"] = WORLD_MERC_MAX - tile_merc_size * y
    return bbox


def bbox_to_sql(bbox: dict) -> str:
    DENSIFY_FACTOR = 4
    bbox["seg_size"] = (bbox["xmax"] - bbox["xmin"]) / DENSIFY_FACTOR
    sql_tmpl = "ST_Segmentize(ST_MakeEnvelope({xmin}, {ymin}, {xmax}, {ymax}, 3857), {seg_size})"
    return sql_tmpl.format(**bbox)


TILE_RESPONSE_PARAMS: Dict[str, Any] = {
    "responses": {200: {"content": {"application/x-protobuf": {}}}},
    "response_class": Response,
}
