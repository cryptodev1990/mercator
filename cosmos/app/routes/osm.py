"""Open Street Maps (OSM) routes."""
import logging
import uuid
from typing import Any, List
from openai import OpenAIError

import sqlalchemy.exc
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection
from app.crud.entity_resolve import named_place, resolve_entity
from app.crud.executors import category_lookup, raw_lookup

from app.dependencies import get_conn
from app.crud.osm_search import eval_query
from app.parsers.intents import DerivedIntent, ParsedQuery
from app.parsers.openai_icsf.openai_slot_parser import OpenAIParseError

from app.schemas import IntentPayload, OsmRawQueryResponse, ParsedEntity, IntentResponse, ValidIntentNameEnum
from app.parsers.openai_icsf import openai_intent_classifier
from app.models.intent import Intent, intents

router = APIRouter(prefix="")

logger = logging.getLogger(__name__)


@router.get(
    "/query",
    response_model=IntentResponse,
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
) -> IntentResponse:
    """Query OSM.

    This endpoint accepts a natural language query and returns a list of matching features.
    """
    # unique identifier for this query
    intent, inferred_intents = None, []
    inferred_slots = {}
    query_id = uuid.uuid4()
    try:
            # logger.info({"uuid": id_, "query": query})
            print({"uuid": str(query_id), "query": query})
            inferred_intents = openai_intent_classifier(query, intents)
            arg_intent = inferred_intents[0]
            intent = intents[arg_intent]
            print({"uuid": str(query_id), "intent": intent})
            inferred_slots = intent.parse(query)
            num_inferred_slots = len(inferred_slots.keys())
            print({"uuid": str(query_id), "slots": inferred_slots, "num_slots": num_inferred_slots})
            assert num_inferred_slots >= intent.num_slots, f"Parse will not match the executor (saw {num_inferred_slots}, expected {intent.num_slots}"
            derived_intent = DerivedIntent(
                intent=intent,
                args=inferred_slots,
            )
            parsed_query = ParsedQuery(
                value=derived_intent,
                text=query
            )
    except (OpenAIError, OpenAIParseError, AssertionError) as exc:
        logger.warning({"msg": "Unable to parse intents with OpenAI", "query": query,
            "intent": intent, "query_id": query_id, "reason": str(exc)})
        derived_intent = DerivedIntent(
            intent=intents["raw_lookup"],
            args={"IntentResponse": query},
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
    print({"uuid": str(query_id), "results": results})
    return IntentResponse(
        query=query,
        parse_result=results,
        intents=inferred_intents,
        slots=inferred_slots,  # type: ignore
        id=query_id,
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
        example="SELECT * FROM osm WHERE tag @> '{\"name\": \"San Francisco\"}':: JSONB",
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
    "/search",
    response_model=List[ParsedEntity],
    responses={"400": {"description": "Unable to execute search"}},
)
async def _get_search(
    term: str = Query(
        ...,
        example="San Francisco",
        description="Search term.",
    ),
    method: str = Query(
        ...,
        example="fuzzy",
        description="Search method, which can be one of 'fuzzy', 'category', or 'named_place'.",
    ),
    conn: AsyncConnection = Depends(get_conn),
) -> Any:
    if method == "fuzzy":
        entities = await raw_lookup(term, conn=conn)
        return entities.entities
    elif method == "category":
        return await category_lookup([term], conn=conn)
    elif method == "named_place":
        entity = named_place(term)
        return ParsedEntity(
            lookup=entity.lookup,
            match_type=entity.match_type,
            geoids=entity.geoids,
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid search method.")


@router.post(
    "/execute",
    response_model=IntentResponse,
    responses={"400": {"description": "Unable to execute search"}}
)
async def _get_execute(
    intent_payload: IntentPayload = Body(..., example={
        "name": "x_in_y",
        "args": {
            "needle_place_or_amenity": {
                "lookup": "coffee shops",
                "match_type": "fuzzy",
            },
            "haystack_place_or_amenity": {
                "lookup": "San Francisco",
                "match_type": "named_place",
            }
        }
    }),
    conn: AsyncConnection = Depends(get_conn),
):
    query_id = uuid.uuid4()
    execute = Intent.get_execute_method(intent_payload.name)
    # We use this .as_dict() method instead of pydantic's .dict() method because we want to
    # only turn the top-level args into a dict, not the nested args, and we want to
    # remove any None values.
    results = await execute(**intent_payload.args.as_dict(), conn=conn)

    return IntentResponse(
        query="",
        parse_result=results,
        intents=[intent_payload.name],
        slots=intent_payload.args,
        id=query_id,
    )
