"""Open Street Maps (OSM) routes."""
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import NonNegativeInt  # pylint: disable=no-name-in-module
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.core.datatypes import BBoxTuple
from app.dependencies import get_conn
from app.schemas import BaseModel

router = APIRouter(prefix="/search")

logger = logging.getLogger(__name__)


class OsmQueryParse(BaseModel):
    """Parse query."""

    intent: str
    args: Dict[str, Any]


class OsmSearchResponse(BaseModel):
    """Response for OSM search."""

    query: str
    parse: Optional[OsmQueryParse]
    results: Dict[str, Any]


class OsmRawQueryResponse(BaseModel):
    """Response for raw SQL executed against OSM."""

    query: str
    results: List[Dict[str, Any]]


# # pylint: disable=unused-argument
# @router.get("/search", response_model=OsmSearchResponse)
# async def get_shapes_from_osm(
#     query: str = Query(...),
#     bbox: Optional[BBox] = Query(None),
#     limit: NonNegativeInt = Query(20),
#     top_n_figure: NonNegativeInt = Query(10),
#     top_n_ground: NonNegativeInt = Query(10),
#     conn: AsyncConnection = Depends(get_conn),
# ) -> OsmSearchResponse:
#     """Get shapes from OSM by amenity."""
#     parsed = parse_query(query=query)
#     bbox_obj = ViewportBounds.from_list(bbox) if bbox else None
#     res = await run_spatial_relation(
#         conn,
#         figure=parsed["figure"],
#         ground=parsed["ground"],
#         relation=parsed["relation"],
#         bbox=bbox_obj,
#         top_n_figure=top_n_figure,
#         top_n_ground=top_n_ground,
#         limit=limit,
#     )
#     return OsmSearchResponse.parse_obj(
#         {
#             "query": query,
#             "parsed": {
#                 "figure": parsed["figure"],
#                 "relation": parsed["relation"],
#                 "ground": parsed["ground"],
#             },
#             "results": res,
#         }
#     )

QUERY_PAT = re.compile(r"^(?:get )?(?P<subject>.*)\s+(?P<predicate>in)\s+(?P<object>.*)$")


class QueryParseError(Exception):
    """Exception for parsing errors."""

    def __init__(self, query: str) -> None:
        super().__init__()
        self.query = query

    def __str__(self) -> str:
        return f"Unable to parse: {self.query}"


def parse_query(query: str) -> Optional[OsmQueryParse]:
    """Parse query."""
    m = QUERY_PAT.search(query)
    if not m:
        raise QueryParseError(query)

    return OsmQueryParse.parse_obj(
        {
            "intent": "spatial_relation",
            "args": {
                "subject": {
                    "text": m.group("subject"),
                    "start": m.start("subject"),
                    "end": m.end("subject"),
                },
                "predicate": {
                    "relation": "IN",
                    "text": m.group("predicate"),
                    "start": m.start("predicate"),
                    "end": m.end("predicate"),
                },
                "object": {
                    "text": m.group("object"),
                    "start": m.start("object"),
                    "end": m.end("object"),
                },
            },
        }
    )


@router.get(
    "/v0/",
    response_model=OsmSearchResponse,
    responses={"400": {"description": "Unable to parse query."}},
)
async def _search(
    query: str = Query(..., description="Query text string"),
    bbox: BBoxTuple = Query(
        [-180, -90, 180, 90],
        description="Bounding box to restrict the search: min_lon, min_lat, max_lon, max_lat",  # pylint: disable=line-too-long
    ),
    limit: NonNegativeInt = Query(20, description="Maximum number of results to return"),
    conn: AsyncConnection = Depends(get_conn),
) -> Any:
    """Query OSM.

    The query must be in the form of: "Get <amenity> in <place>",
    where `<amenity>` is the amenity to search for and `<place>` is a
    geographic area, e.g. a city or a country.

    For example:

    - "Get coffee shops in San Francisco"
    - "Coffee shops in Oakland"

    """
    # Split query into parts separated by in
    parse = parse_query(query)
    if parse is None:
        raise HTTPException(status_code=400, detail="Unable to parse query.")

    # the current query is specialized
    stmt = text(
        """
        WITH objs AS (
            SELECT
                ST_BuildArea(geom) AS geom
            FROM osm
            WHERE TRUE
                AND category = 'boundary'
                AND fts @@ websearch_to_tsquery(:obj_text)
            ORDER BY ST_Area(ST_Transform(ST_BuildArea(geom), 3857)) DESC
            LIMIT 5
        )
        , matches AS (
            SELECT
                osm.geom,
                osm.tags,
                osm.osm_id,
                osm.osm_type
            FROM osm
            INNER JOIN objs AS o
                ON ST_Contains(o.geom, osm.geom)
                AND osm.category = 'point'
                AND fts @@ websearch_to_tsquery(:subj_text)
            LIMIT :limit
        )
        , agg AS (
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
                ) AS features,
                ST_Extent(geom) AS bbox
            FROM matches
        )
        SELECT
            jsonb_build_object(
                'type', 'FeatureCollection',
                'features', coalesce(features, jsonb_build_array()),
                'bbox', jsonb_build_array(
                    ST_XMin(bbox), ST_YMin(bbox), ST_XMax(bbox), ST_YMax(bbox)
                )
            ) AS feature_collection
        FROM agg
        """
    )
    params = {
        "subj_text": parse.args["subject"]["text"],
        "obj_text": parse.args["object"]["text"],
        "limit": limit,
        **dict(zip(("xmin", "ymin", "xmax", "ymax"), bbox)),
    }
    res = await conn.execute(stmt, params)
    results = res.scalar()
    return OsmSearchResponse(query=query, parse=parse, results=results)



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
    results = [dict(row._mapping) for row in res.fetchall()]
    return OsmRawQueryResponse(query=query, results=results)
