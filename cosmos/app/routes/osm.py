"""Open Street Maps (OSM) routes."""
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import NonNegativeInt  # pylint: disable=no-name-in-module
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.core.datatypes import BBox, FeatureCollection
from app.crud.osm_search import sprel_query_stmt
from app.dependencies import get_conn
from app.parsers.regex import parse
from app.schemas import (
    Location,
    OsmRawQueryResponse,
    OsmSearchResponse,
    SpRelCoveredBy,
    SpRelDisjoint,
)

router = APIRouter(prefix="")

logger = logging.getLogger(__name__)


@router.get(
    "/query",
    response_model=OsmSearchResponse,
    responses={"400": {"description": "Unable to parse query."}},
)
async def _get_query(
    query: str = Query(..., description="Query text string."),
    bbox: BBox = Query(
        (-180, -90, 180, 90),
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
    parsed_query = parse(query)
    if parsed_query is None:
        raise HTTPException(status_code=400, detail="Unable to parse query.")

    # semantic analysis of the parse tree to convert it into a SQL query
    params = {"location": parsed_query["args"]["subject"]["text"]}
    if parsed_query.get("intent") == "covered_by":
        obj_query = parsed_query["args"]["object"]["text"]
        params["relations"] = [SpRelCoveredBy(location=Location(query=obj_query, bbox=bbox))]
    elif parsed_query.get("intent") == "disjoint":
        obj_query = parsed_query["args"]["object"]["text"]
        params["relations"] = [SpRelDisjoint(location=Location(query=obj_query, bbox=bbox))]

    label_args = [parsed_query["args"]["subject"]["text"]]
    if parsed_query.get("intent") in {"contains", "disjoint"}:
        label_args.append(parsed_query["args"]["predicate"]["text"])
        label_args.append(parsed_query["args"]["object"]["text"])
    label = " ".join(label_args)
    sql = sprel_query_stmt(**params, bbox=bbox, limit=limit)

    results = await conn.execute(sql)
    return OsmSearchResponse(
        query=query,
        label=label,
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
    query: str = Query(..., description="Query text string"),
    conn: AsyncConnection = Depends(get_conn),
) -> Any:
    """Query OSM.
    This executes raw SQL against the local or hosted OSM postgres instance.
    If the query client user has write access, you may have a very bad time.
    """
    res = await conn.execute(text(query))
    results = [dict(row._mapping) for row in res.fetchall()]  # pylint: disable=protected-access
    return OsmRawQueryResponse(query=query, results=results)
