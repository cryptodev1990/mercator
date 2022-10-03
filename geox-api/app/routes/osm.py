"""Open Street Maps (OSM) routes."""
from typing import List

from app.dependencies import get_osm_conn
from fastapi import APIRouter, Depends
from geojson_pydantic import Feature
from sqlalchemy import text
from sqlalchemy.engine import Connection

router = APIRouter(tags=["osm"])


@router.get("/osm")
async def get_shapes_from_osm(query: str, geographic_reference: str, conn: Connection = Depends(get_osm_conn)) -> List[Feature]:
    """Get shapes from OSM by amenity."""
    res = conn.execute(
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
