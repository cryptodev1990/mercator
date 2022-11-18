"""Routes for the Voyager API used to query OSM."""
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from fastapi import APIRouter, Depends, Query
from geojson_pydantic import FeatureCollection
from geojson_pydantic.geometries import Geometry
from pydantic import NonNegativeInt # pylint: disable=no-name-in-module
from sqlalchemy import String, func, select, or_
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import ColumnElement, Join, Select, cast
from sqlalchemy.sql.expression import CTE

from app.core.datatypes import BBoxTuple
from app.data.feature_classes import FeatureClass, feature_classes
from app.db import osm as osm_tbl
from app.dependencies import get_conn
from app.schemas import LocationQuery, SpatialRelation

router = APIRouter(prefix="/voyager")

logger = logging.getLogger(__name__)


def _in_bbox(
    col: ColumnElement, bbox: Tuple[float, float, float, float], srid: int = 4326
) -> ColumnElement:
    """Return where clause for bounding box."""
    return func.ST_Intersects(col, func.ST_MakeEnvelope(*bbox, srid))


def _select_osm_stmt(
    *,
    class_name: Optional[str] = None,
    id_: Optional[int] = None,
    bbox: Optional[BBoxTuple] = None,
    limit: Optional[int] = None,
    osm_type: Optional[str] = None,
    osm_category: Optional[str] = None,
    cols: Optional[List[ColumnElement[Any]]] = None,
) -> select:
    if cols is None:
        cols = [
            osm_tbl.c.osm_id,
            osm_tbl.c.osm_type,
            osm_tbl.c.category,
            osm_tbl.c.tags,
            osm_tbl.c.geom,
        ]
    stmt = select(cols).select_from(osm_tbl).limit(limit)  # type: ignore
    if class_name:
        _kls = feature_classes[class_name]
        stmt = stmt.where(osm_tbl.c.tags.op("->>")(_kls.key) == _kls.value)  # type: ignore
    if bbox:
        stmt = stmt.where(_in_bbox(osm_tbl.c.geom, bbox))  # type: ignore
    if id_:
        stmt = stmt.where(osm_tbl.c.osm_id == id_)  # type: ignore
    if osm_type:
        stmt = stmt.where(osm_tbl.c.osm_type == osm_type)
    if osm_category:
        stmt = stmt.where(osm_tbl.c.category == osm_category)
    return stmt


def _sprel_query(
    *,
    class_name: Optional[str] = None,
    id_: Optional[int] = None,
    bbox: Optional[BBoxTuple] = None,
    relations: Optional[List[SpatialRelation]] = None,
    limit: Optional[int] = 10,
) -> Select:
    base: Select = _select_osm_stmt(class_name=class_name, id_=id_, bbox=bbox)

    rel_ctes = []
    # for each relation, create a CTE
    for i, rel in enumerate(relations or []):
        rel_stmt = _select_osm_stmt(
            id_=rel.location.id_ if rel.location else None,
            class_name=(rel.location.class_name if rel.location else None),
            bbox=(rel.location.bbox if rel.location else None) or bbox,
        )
        if rel.type == "in":
            rel_stmt = rel_stmt.where(
                or_(func.ST_GeometryType(osm_tbl.c.geom).in_(["ST_Polygon", "ST_MultiPolygon"]),
                     osm_tbl.c.category == "boundary")
            )
        elif rel.type == "crosses":
            rel_stmt = rel_stmt.where(
                func.ST_GeometryType(osm_tbl.c.geom).in_(
                    ["ST_Polygon", "ST_MultiPolygon", "ST_Line", "ST_MultiLine"]
                )
            )
            base = base.where(func.ST_GeometryType(base.c.geom).in_(["ST_Line", "ST_MultiLine"]))
        rel_ctes.append((rel, rel_stmt.cte(f"rel_{i}")))

    # Make base a CTE after it has been modified
    base_cte = base.cte("base")
    # Now start a join clause
    join_clause: Union[Join, CTE] = base_cte
    # Now merge with the rel CTEs
    for i, (rel, cte) in enumerate(rel_ctes):
        if rel.type == "in":
            join_clause = join_clause.join(cte,
                                           func.case(
                                               (cte.c.category == "boundary",
                                                func.ST_CoveredBy(base_cte.c.geom, func.ST_BuildArea(cte.c.geom))),
                                                else_=func.ST_CoveredBy(base_cte.c.geom, cte.c.geom)
                                            ))
        elif rel.type == "crosses":
            join_clause = join_clause.join(cte, func.ST_Intersects(base_cte.c.geom, cte.c.geom))
        elif rel.type == "borders":
            join_clause = join_clause.join(cte, func.ST_Touches(base_cte.c.geom, cte.c.geom))
            # TODO: add constraints to ensure that the two geometries are consistent
        elif rel.type == "distance":
            if rel.relation == ">":
                join_clause = join_clause.join(
                    cte, func.ST_Distance(base_cte.c.geom, cte.c.geom) > rel.value
                )
            elif rel.relation == "<":
                join_clause = join_clause.join(
                    cte, func.ST_Dwithin(base_cte.c.geom, cte.c.geom, rel.value)
                )
        elif rel.type == "direction":
            join_clause = join_clause.join(
                cte, func.ST_GetDirection(base_cte.c.geom, cte.c.geom) == rel.direction
            )
        else:
            raise NotImplementedError(f"Relation type {rel.type} not implemented")

    # final query
    stmt = (
        select(
            func.to_geojson_feature(
                base_cte.c.geom,
                func.jsonb_build_object(
                    "osm",
                    func.jsonb_build_object(
                        "tags",
                        base_cte.c.tags,
                        "type",
                        base_cte.c.osm_type,
                        "id",
                        base_cte.c.osm_id,
                        "category",
                        base_cte.c.category,
                    ),
                ),
                cast(base_cte.c.osm_id, String()),
            ).label("feature")
        )
        .select_from(join_clause)
        .limit(limit)
    )
    return stmt


@router.post("/osm/entities/search", response_model=FeatureCollection[Geometry, Dict[str, Any]])
async def get_osm_search(
    body: LocationQuery,
    limit: int = Query(10, ge=1),
    conn: AsyncConnection = Depends(get_conn),
) -> FeatureCollection[Geometry, Dict[str, Any]]:
    """Query OSM enttities with spatial relation constraints."""
    # the current query is specialized
    base = _sprel_query(
        class_name=body.class_name,
        bbox=body.bbox,
        relations=body.relations,
        limit=limit,
    )
    # stmt = select(func.to_geojson_feature(base.c.geom, base.c.tags, cast(base.c.osm_id, String)))
    stmt = base
    res = await conn.execute(stmt)
    return FeatureCollection.parse_obj(
        {"features": [row.feature for row in res], "type": "FeatureCollection"}
    )


@router.get("/osm/entities", response_model=FeatureCollection[Geometry, Dict[str, Any]])
async def get_osm_entities(
    query: str = Query(None, alias="q", description="Query text string"),
    name: str = Query(None, description="Name of the location"),
    osm_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    bbox: BBoxTuple = Query(
        (-180, -90, 180, 90),
        description="Bounding box to restrict the search: min_lon, min_lat, max_lon, max_lat",  # pylint: disable=line-too-long
    ),
    limit: NonNegativeInt = Query(20, description="Maximum number of results to return"),
    conn: AsyncConnection = Depends(get_conn),
) -> FeatureCollection[Geometry, Dict[str, Any]]:
    """Query OSM."""
    # the current query is specialized
    base = _select_osm_stmt(osm_type=osm_type, osm_category=category, bbox=bbox, limit=limit)
    if query:
        base = base.where(osm_tbl.c.fts.op("@@")(func.websearch_to_tsquery(query)))
    if name:
        base = base.where(osm_tbl.c.tags["name"] == name)
    # stmt = select(func.to_geojson_feature(base.c.geom, base.c.tags, cast(base.c.osm_id, String)))
    stmt = select(
        func.to_geojson_feature(
            base.c.geom,
            func.jsonb_build_object(
                "osm",
                func.jsonb_build_object(
                    "tags",
                    base.c.tags,
                    "type",
                    base.c.osm_type,
                    "id",
                    base.c.osm_id,
                    "category",
                    base.c.category,
                ),
            ),
            cast(base.c.osm_id, String()),
        ).label("feature")
    )
    res = await conn.execute(stmt)
    return FeatureCollection.parse_obj({"features": [row.feature for row in res]})


@router.get("/osm/class-lexicon", response_model=Dict[str, FeatureClass])
async def _osm_classes() -> Dict[str, FeatureClass]:
    """List of words that can be matched to OSM feature classes.

    For example: restaurant, pub.
    """
    return feature_classes
