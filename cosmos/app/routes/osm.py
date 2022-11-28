"""Open Street Maps (OSM) routes."""
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import NonNegativeInt  # pylint: disable=no-name-in-module
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.core.datatypes import BBox, FeatureCollection
from app.crud.osm_search import to_sql
from app.dependencies import get_conn
from app.parsers.exceptions import QueryParseError
from app.parsers.rules import parse
from app.schemas import OsmRawQueryResponse, OsmSearchResponse

router = APIRouter(prefix="")

logger = logging.getLogger(__name__)


@router.get(
    "/query",
    response_model=OsmSearchResponse,
    responses={"400": {"description": "Unable to parse query."}},
)
async def _get_query(
    query: str = Query(
        ..., example="Coffee shops in San Francisco", description="Query text string."
    ),
    bbox: BBox = Query(
        (-180, -90, 180, 90),
        example=[-124.5, 32.6, -114.2, 42.1],
        description="Bounding box to restrict the search: min_lon, min_lat, max_lon, max_lat",  # pylint: disable=line-too-long
    ),
    limit: NonNegativeInt = Query(20, description="Maximum number of results to return"),
    conn: AsyncConnection = Depends(get_conn),
) -> OsmSearchResponse:
    """Query OSM.

    This endpoint accepts a natural

    It currently supports:

    - "*spatial feature*", which searches OSM for a spatial feature using full-text search.
    - "*features_1* in *features_2*", which constrains results  which constrains results to
        the search results in *features_1* that are contained in any of the search results
        of *feature_2*.
    - "*features_1* not in *features_2*" which constrains results to features matches by the
        search in *features_1* that are not contained in *feature_2*.

    Examples:

    - coffee shops in San Francisco
    - Coffee shops in Oakland
    - Coffee shops
    - Coffee shops not in Oakland

    """
    try:
        parsed_query = parse(query)
    except QueryParseError:
        raise HTTPException(status_code=422, detail="Unable to parse query.") from None

    sql = to_sql(parsed_query, bbox=bbox, limit=limit)
    results = await conn.execute(sql)

    return OsmSearchResponse(
        query=query,
        label=str(parsed_query),
        parse=parsed_query,
        results=FeatureCollection(features=[row.feature for row in results]),  # type: ignore
    )


@router.get(
    "/sql",
    response_model=OsmRawQueryResponse,
    responses={"400": {"description": "Unable to run SQL query."}},
)
@router.get(
    "/raw-query",
    response_model=OsmRawQueryResponse,
    deprecated=True,
    responses={"400": {"description": "Unable to run SQL query."}},
)
async def _get_raw_query(
    query: str = Query(
        ...,
        example="SELECT * FROM osm WHERE tags->>'name' = 'San Francisco' and category = 'boundary'",
        description="Query text string",
    ),
    conn: AsyncConnection = Depends(get_conn),
) -> Any:
    """Query OSM.
    This executes raw SQL against the local or hosted OSM postgres instance.
    If the query client user has write access, you may have a very bad time.
    """
    res = await conn.execute(text(query))
    results = [dict(row._mapping) for row in res.fetchall()]  # pylint: disable=protected-access
    return OsmRawQueryResponse(query=query, results=results)
