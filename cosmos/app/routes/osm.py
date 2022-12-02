"""Open Street Maps (OSM) routes."""
import logging
from typing import Any

import sqlalchemy.exc
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import NonNegativeInt  # pylint: disable=no-name-in-module
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.core.datatypes import BBox, FeatureCollection
from app.crud.osm_search import eval_query
from app.dependencies import get_conn
from app.parsers.exceptions import QueryParseError
from app.parsers.rules import parse
from app.schemas import OsmRawQueryResponse, OsmSearchResponse

router = APIRouter(prefix="")

logger = logging.getLogger(__name__)


@router.get(
    "/query",
    response_model=OsmSearchResponse,
    responses={
        "400": {"description": "Unable to parse query."},
        "504": {"description": "Query timed out."},
    },
)
async def _get_query(
    query: str = Query(
        ..., example="Coffee shops in San Francisco", description="Query text string."
    ),
    bbox: BBox = Query(
        None,
        example=[-124.5, 32.6, -114.2, 42.1],
        description="Bounding box to restrict the search: min_lon, min_lat, max_lon, max_lat",  # pylint: disable=line-too-long
    ),
    limit: NonNegativeInt = Query(100, description="Maximum number of results to return"),
    offset: NonNegativeInt = Query(0, description="Offset into the results"),
    conn: AsyncConnection = Depends(get_conn),
) -> OsmSearchResponse:
    """Query OSM.

    This endpoint accepts a natural language query and returns a list of matching features.

    It currently supports queries like:

    - "San Francisco"
    - "Coffee shops"
    - "Coffee shops in San Francisco"
    - "Coffee shops not in San Francisco"
    - "Restaurants near Lake Merritt"
    - "Restaurants not near Lake Merritt"
    - "Restaurants within 10 miles of Lake Merritt"
    - "Restaurants more than 10 miles from Lake Merritt"
    - "Draw an isochrone of 10 minutes around Lake Merritt"
    - "Cafes within 10 minutes of Lake Merritt"
    - "Cafes more than 10 minutes from Lake Merritt"
    - "Route from Lake Merritt to the Ferry Building"

    """
    try:
        parsed_query = parse(query)
    except QueryParseError as exc:
        raise HTTPException(status_code=422, detail=f"Unable to parse query: {exc}") from None
    try:
        results = await eval_query(parsed_query, bbox=bbox, limit=limit, conn=conn, offset=offset)
    except sqlalchemy.exc.DBAPIError as exc:
        if "canceling statement due to statement timeout" in str(exc.orig):
            raise HTTPException(status_code=504, detail="Query timed out.") from None
        raise exc
    return OsmSearchResponse(
        query=query,
        label=str(parsed_query),
        parse=parsed_query,
        results=results or FeatureCollection(features=[]),  # type: ignore
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
