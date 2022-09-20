from typing import Any, Dict, List, Tuple

from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
from geojson_pydantic import Feature
from sqlalchemy import text

from app.db.session import OsmSessionLocal
from app.routes.tile_utils import (
    tile_to_envelope,
    bbox_to_sql,
    TILE_RESPONSE_PARAMS,
)
router = APIRouter(tags=["osm"])


def point_in_box(point, bounding_box: List[float]) -> bool:
    """
    Check if a point is in a bounding box.
    """
    return (
        point["geometry"]["coordinates"][0] >= bounding_box[0]
        and point["geometry"]["coordinates"][0] <= bounding_box[2]
        and point["geometry"]["coordinates"][1] >= bounding_box[1]
        and point["geometry"]["coordinates"][1] <= bounding_box[3]
    )


@router.get("/osm")
async def get_shapes_from_osm(query: str, geographic_reference: str) -> List[Feature]:
    """Get shapes from OSM by amenity"""
    if OsmSessionLocal is None:
        raise Exception()  # TODO: need an exception for this
    with OsmSessionLocal() as db_osm:
        res = db_osm.execute(
            text(
                """
           WITH container AS (
              SELECT geom
              FROM (
                SELECT ST_BuildArea(geom) AS geom
                FROM boundaries
                WHERE fts @@ websearch_to_tsquery(:geographic_reference)
                LIMIT 5
              ) candidates
              ORDER BY ST_Area(geom) DESC
              LIMIT 1
            )
            SELECT
              ST_AsGeoJSON(ST_Transform(points.geom, 4326)) as geometry
            , json_build_object(
              'name', tags->>'name',
              'amenity', tags->>'amenity') as properties
            FROM points
            JOIN container
            ON ST_CONTAINS(container.geom, points.geom)
            WHERE 1=1
              AND fts @@ websearch_to_tsquery(:query)
              """
            ),
            {"query": query, "geographic_reference": geographic_reference},
        )
        rows = res.mappings().all()
        return [Feature(**row) for row in rows] if len(rows) > 0 else []


@router.get("/osm/ways/")
async def get_roads_by_bounding_box(
    xmin: float, ymin: float, xmax: float, ymax: float, shape_to_snap: Feature
):
    if OsmSessionLocal is None:
        raise Exception  # TODO: need an exception for this
    with OsmSessionLocal() as db_osm:
        db_osm.execute(
            text(
                """
        WITH all_ways AS (
        SELECT way
        FROM planet_osm_roads
        WHERE 1=1
          AND ST_Intersects(
            way,
            ST_MakeEnvelope(
                :xmin, :ymin,
                :xmax, :ymax,
                3857)
          )
        )
        """,
                {"xmin": xmin, "ymin": ymin, "xmax": xmax,
                    "ymax": ymax},  # type: ignore
            )
        )


@router.get("/osm/{z}/{x}/{y}.pbf", **TILE_RESPONSE_PARAMS)
def get_tiles(response: Response, z: float, x: float, y: float):
    if OsmSessionLocal is None:
        raise Exception("OSM features not available")

    if z > 15:
        size = 2**z
        if x >= size or y >= size or x < 0 or y < 0:
            raise Exception("Request is invalid")
        bbox = tile_to_envelope(x, y, z)
        bbox_sql = bbox_to_sql(bbox)
        sql = f"""
    WITH
    bounds AS (
      SELECT {bbox_sql} AS geom
      , {bbox_sql}::box2d AS b2d
    )
    , mvtgeom AS (
      SELECT ST_AsMVTGeom(
        ST_Transform(t.geom, 3857) , bounds.b2d
      ) AS geom
      , tags
      FROM points p
      CROSS JOIN bounds
      WHERE ST_Intersects(p.geom, ST_Transform(bounds.geom, 3857))
    )
    SELECT ST_AsMVT(mvtgeom.*) FROM mvtgeom
    """
        with OsmSessionLocal() as db_osm:
            res = db_osm.execute(sql)
            rows = res.mappings().fetchone()
            return Response(
                media_type="application/x-protobuf", content=bytes(rows["st_asmvt"])
            )
