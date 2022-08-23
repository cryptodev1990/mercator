# import aiohttp

from typing import List, Tuple

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from geojson_pydantic import Feature
from sqlalchemy import text

from app.db.session import OsmSessionLocal

router = APIRouter(tags=["geofencer", "osm"])


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
        raise Exception   # TODO: need an exception for this
    with OsmSessionLocal() as db_osm:
        res = db_osm.execute(
            text(
                """
           WITH container AS (
              SELECT ST_BuildArea(geom) AS geom
              FROM boundaries
              WHERE fts @@ websearch_to_tsquery(:geographic_reference)
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
              """,
                dict(query=query, geographic_reference=geographic_reference),
            )
        )
        rows = res.mappings().all()
        return [Feature(**row) for row in rows] if len(rows) > 0 else []


@router.get("/osm/ways/")
async def get_roads_by_bounding_box(
    xmin: float, ymin: float, xmax: float, ymax: float, shape_to_snap: Feature
):
    if OsmSessionLocal is None:
        raise Exception   # TODO: need an exception for this
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
                {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax},
            )
        )


@router.get("/osm/isochrone")
async def isochrone(
    latlngs: List[Tuple[float]], time_in_minutes: float, profile: str
):
    # https://docs.graphhopper.com/#tag/Isochrone-API
    """Get shapes from OSM by amenity"""
    # TODO: implement
    # Maybe to best with a celery worker?
    BASE_ROUTE = "https://graphhopper.com/api/1/isochrone"
    # async def get(url, datum, session):
    #     try:
    #         async with session.get(url=BASE_ROUTE, params={
    #           "point": datum["point"],
    #           "time": time_in_minutes,
    #           "profile": profile,
    #         }) as response:
    #             resp = await response.read()
    #     except Exception as e:
    #         print("Unable to get url {} due to {}.".format(url, e.__class__))

    # async with aiohttp.ClientSession() as session:
    #     ret = await asyncio.gather(*[get(url, session) for url in urls])

    # asyncio.run(get(url, session))
