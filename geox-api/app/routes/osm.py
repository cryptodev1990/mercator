"""Open Street Maps (OSM) routes."""
from typing import List

from fastapi import APIRouter
from geojson_pydantic import Feature
from sqlalchemy import text

from app.db.osm import OsmSessionLocal

router = APIRouter(tags=["osm"])


@router.get("/osm")
async def get_shapes_from_osm(query: str, geographic_reference: str) -> List[Feature]:
    """Get shapes from OSM by amenity."""
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
