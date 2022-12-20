"""Open Street Maps (OSM) routes."""
import logging
import uuid
from typing import Any
from openai import OpenAIError

import sqlalchemy.exc
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import NonNegativeInt  # pylint: disable=no-name-in-module
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.core.datatypes import BBox, FeatureCollection
from app.dependencies import get_conn
from app.crud.osm_search import eval_query
from app.parsers.intents import OpenAIDerivedIntent, ParsedQuery

from app.schemas import OsmRawQueryResponse, OsmSearchResponse, OsmShapeForIdResponse
from app.parsers.openai_icsf import openai_intent_classifier, openai_slot_fill
from app.models.intent import intents

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

    It currently supports the following queries:

    - named places: "San Francisco"
    - places: "Coffee shops"
    - X in Y: "Coffee shops in San Francisco"
    - X not in Y: "Coffee shops not in San Francisco"
    - X near Y: "Restaurants near Lake Merritt"
    - X not near Y: "Restaurants not near Lake Merritt"
    - X within distance of Y: "Restaurants within 10 miles of Lake Merritt"
    - X not within distance of Y: "Restaurants more than 10 miles from Lake Merritt"
    - X within time of Y: "Cafes within 10 minutes of Lake Merritt"
    - X not within time of Y: "Cafes not within 10 minutes of Lake Merritt"
    - Buffer of time around Y: "Buffer of 10 minutes around Lake Merritt"
    - Buffer of distance around Y: "Buffer of 10 miles around Lake Merritt"
    - Route from X to Y: "Route from Lake Merritt to the Ferry Building"

    """
    # unique identifier for this query
    id_ = uuid.uuid4()
    try:
            # logger.info({"uuid": id_, "query": query})
            print({"uuid": str(id_), "query": query})
            inferred_intents = openai_intent_classifier(query, intents)
            arg_intent = inferred_intents[0]
            intent = intents[arg_intent]
            print({"uuid": str(id_), "intent": intent})
            inferred_slots = intent.parse(query)
            print({"uuid": str(id_), "slots": inferred_slots})
            derived_intent = OpenAIDerivedIntent(
                intent=intent,
                args=inferred_slots,
            )
            parsed_query = ParsedQuery(
                value=derived_intent,
                text=query
            )
    except OpenAIError as exc:
        logger.warning("Unable to parse query: {exc}")
        derived_intent = OpenAIDerivedIntent(
            intent="raw_lookup",
            args={"search_term": query},
        )
        parsed_query = ParsedQuery(
            value=derived_intent,
            text=query
        )
    try:
        results = await eval_query(parsed_query, conn=conn)
    except sqlalchemy.exc.DBAPIError as exc:
        if "canceling statement due to statement timeout" in str(exc.orig):
            raise HTTPException(status_code=504, detail="Query timed out.") from None
        raise exc
    return OsmSearchResponse(
        query=query,
        label=str(parsed_query),
        parse=parsed_query,
        results=results,  # type: ignore
        id=id_,
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


@router.get(
    "/shape_for_id",
    response_model=OsmShapeForIdResponse,
    responses={"400": {"description": "Unable to run SQL query."}},
)
async def _get_shape_for_id(
    osm_id: int = Query(
        ...,
        example=42298798,
        description="OSM id.",
    ),
    conn: AsyncConnection = Depends(get_conn),
) -> Any:
    """Query OSM for a specific ID and return in the Feature struct.
    Note that the core /query API returns a List[Feature]. Mimick
    that struct for simplicity, except in this case we only ever have a single
    row/Feature per queried OSM id.

    ToDo: Possibly switch this to SQL Builder API as in ../crud/osm_search.py et al.
    """
    stmt = text(
        """
        SELECT
            jsonb_agg(
                jsonb_build_object(
                    'type', 'Feature',
                    'geometry', ST_AsGeoJSON(geom) :: JSONB,
                    'properties', jsonb_build_object(
                        'osm', jsonb_build_object(
                            'tags', tags,
                            'type', osm_type,
                            'id', osm_id
                        )
                    ),
                    'id', osm_id,
                    'bbox', jsonb_build_array(
                        ST_XMin(geom), ST_YMin(geom), ST_XMax(geom), ST_YMax(geom)
                    )
                )
            ) AS features
        FROM osm
        WHERE TRUE
            AND osm_id = :osm_id
        """
    )

    params = {
        "osm_id": osm_id,
    }

    res = await conn.execute(stmt, params)
    result = res.scalar()
    assert(len(result) == 1)
    return OsmShapeForIdResponse(osm_id=osm_id, result=result[0])
