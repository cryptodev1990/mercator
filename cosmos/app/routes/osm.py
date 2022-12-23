"""Open Street Maps (OSM) routes."""
import logging
import uuid
from typing import Any
from openai import OpenAIError

import sqlalchemy.exc
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.dependencies import get_conn
from app.crud.osm_search import eval_query
from app.parsers.intents import OpenAIDerivedIntent, ParsedQuery
from app.parsers.openai_icsf.openai_slot_parser import OpenAIParseError

from app.schemas import OsmRawQueryResponse, OsmShapeForIdResponse, SearchResponse
from app.parsers.openai_icsf import openai_intent_classifier, openai_slot_fill
from app.models.intent import Intent, intents

router = APIRouter(prefix="")

logger = logging.getLogger(__name__)


@router.get(
    "/query",
    response_model=SearchResponse,
    responses={
        "400": {"description": "Unable to parse query."},
        "504": {"description": "Query timed out."},
    },
)
async def _get_query(
    query: str = Query(
        ..., example="Coffee shops in San Francisco", description="Query text string."
    ),
    conn: AsyncConnection = Depends(get_conn),
) -> SearchResponse:
    """Query OSM.

    This endpoint accepts a natural language query and returns a list of matching features.
    """
    # unique identifier for this query
    intent, inferred_intents = None, []
    inferred_slots = {}
    id_ = uuid.uuid4()
    try:
            # logger.info({"uuid": id_, "query": query})
            print({"uuid": str(id_), "query": query})
            inferred_intents = openai_intent_classifier(query, intents)
            arg_intent = inferred_intents[0]
            intent = intents[arg_intent]
            print({"uuid": str(id_), "intent": intent})
            inferred_slots = intent.parse(query)
            num_inferred_slots = len(inferred_slots.keys())
            print({"uuid": str(id_), "slots": inferred_slots, "num_slots": num_inferred_slots})
            assert num_inferred_slots >= intent.num_slots, "Parse will not match the executor"
            derived_intent = OpenAIDerivedIntent(
                intent=intent,
                args=inferred_slots,
            )
            parsed_query = ParsedQuery(
                value=derived_intent,
                text=query
            )
    except (OpenAIError, OpenAIParseError, AssertionError) as exc:
        logger.warning({"msg": "Unable to parse intents with OpenAI", "query": query,
                        "intent": intent, "query_id": id_})
        derived_intent = OpenAIDerivedIntent(
            intent=intents["raw_lookup"],
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
            await conn.close()
            raise HTTPException(status_code=504, detail="Query timed out.") from None
        raise exc
    print({"uuid": str(id_), "results": results})
    return SearchResponse(
        query=query,
        parse_result=results,
        intents=inferred_intents,
        slots=inferred_slots,  # type: ignore
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
        example="SELECT * FROM osm WHERE tags->>'name' = 'San Francisco'",
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
    assert(len(result) == 1)  # type: ignore
    return OsmShapeForIdResponse(osm_id=osm_id, result=result[0])  # type: ignore
