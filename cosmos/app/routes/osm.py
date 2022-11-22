"""Open Street Maps (OSM) routes."""
import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import NonNegativeInt  # pylint: disable=no-name-in-module
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection
from geojson_pydantic import FeatureCollection

from app.core.datatypes import BBoxTuple
from app.crud.osm_search import sprel_query_stmt
from app.dependencies import get_conn
from app.schemas import Location, SpRelCoveredBy, SpRelDisjoint
from app.parsers.regex import parse

from app.schemas import OsmSearchResponse, OsmRawQueryResponse

router = APIRouter(prefix="/search")

logger = logging.getLogger(__name__)


@router.get(
    "v0",
    response_model=OsmSearchResponse,
    responses={"400": {"description": "Unable to parse query."}},
)
async def _osm_search_v1(
    query: str = Query(..., description="Query text string"),
    bbox: BBoxTuple = Query(
        [-180, -90, 180, 90],
        description="Bounding box to restrict the search: min_lon, min_lat, max_lon, max_lat",  # pylint: disable=line-too-long
    ),
    limit: NonNegativeInt = Query(20, description="Maximum number of results to return"),
    conn: AsyncConnection = Depends(get_conn),
) -> OsmSearchResponse:
    """Query OSM.

    The query must be in the form of:

    - "<location>"
    - "Get <location> in <location>"
    - "Get <location> not <location>"

    where `<location>` are matching entities from a full-text query on OSM.

    For example:

    - "Get coffee shops in San Francisco"
    - "Coffee shops in Oakland"
    - "Coffee shops"
    - "Coffee shops not in Oakland"

    """
    # Split query into parts separated by in
    parsed_query = parse(query)
    if parsed_query is None:
        raise HTTPException(status_code=400, detail="Unable to parse query.")

    params = {"location": parsed_query["args"]["subject"]["text"]}
    if parsed_query.get("intent") == "covered_by":
        obj_query = parsed_query["args"]["object"]["text"]
        params["relations"] = [
            SpRelCoveredBy(location=Location(query=obj_query, bbox=bbox))
        ]
    elif parsed_query.get("intent") == "disjoint":
        obj_query = parsed_query["args"]["object"]["text"]
        params["relations"] = [
            SpRelDisjoint(location=Location(query=obj_query, bbox=bbox))
        ]

    label_args = [parsed_query["args"]["subject"]["text"]]
    if parsed_query.get("intent") in {"contains", "disjoint"}:
        label_args.append(parsed_query["args"]["predicate"]["text"])
        label_args.append(parsed_query["args"]["object"]["text"])
    label = " ".join(label_args)

    # the current query is specialized
    # res = await conn.execute(stmt, params)
    sql = sprel_query_stmt(**params, bbox=bbox, limit=limit)
    results = await conn.execute(sql)
    return OsmSearchResponse(
        query=query,
        label=label,
        parse=parsed_query,
        results=FeatureCollection(features=[row.feature for row in results]) # type: ignore
    )


@router.get(
    "/raw_query/",
    response_model=OsmRawQueryResponse,
    responses={"400": {"description": "Unable to query OSM."}},
)
async def _query_osm(
    query: str = Query(..., description="Query text string"),
    conn: AsyncConnection = Depends(get_conn),
) -> Any:
    """Query OSM.
    This executes raw SQL against the local or hosted OSM postgres instance.
    If the query client user has write access, you may have a very bad time.
    """
    res = await conn.execute(text(query))
    results = [dict(row._mapping) for row in res.fetchall()] # pylint: disable=protected-access
    return OsmRawQueryResponse(query=query, results=results)
