"""OSM search functions."""
import logging
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple, Union

from fastapi import APIRouter, Depends, Query
from geojson_pydantic import FeatureCollection
from geojson_pydantic.geometries import Geometry
from pydantic import NonNegativeInt  # pylint: disable=no-name-in-module
from sqlalchemy import String, and_
from sqlalchemy import case as sql_case
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import ColumnElement, Join, Select, cast
from sqlalchemy.sql.expression import CTE

from app.core.datatypes import BBoxTuple, ViewportBounds
from app.data.feature_classes import FeatureClass, feature_classes
from app.db import osm as osm_tbl
from app.dependencies import get_conn
from app.schemas import SpatialRelation

logger = logging.getLogger(__name__)


class MapProjection(int, Enum):
    WGS84 = 4326
    WEB_MERCATOR = 3857


def _in_bbox(
    col: ColumnElement,
    bbox: Union[Tuple[float, float, float, float], ViewportBounds],
    srid: int = MapProjection.WGS84,
) -> ColumnElement:
    """Return where clause for bounding box."""
    if isinstance(bbox, ViewportBounds):
        envelope = func.ST_MakeEnvelope(bbox.min_x, bbox.min_y, bbox.max_x, bbox.max_y, int(srid))
    envelope = func.ST_MakeEnvelope(*bbox, int(srid))
    return func.ST_Intersects(col, envelope)


# Returns an osm location or locations
def get_osm_location(
    *,
    query: Optional[str] = None,
    bbox: Optional[BBoxTuple] = None,
    limit: Optional[int] = None,
    cols: Optional[List[ColumnElement[Any]]] = None,
) -> select:
    if cols is None:
        cols = [
            osm_tbl.c.osm_id,
            osm_tbl.c.osm_type,
            osm_tbl.c.category,
            osm_tbl.c.tags,
            sql_case(
                (
                    osm_tbl.c.category == "boundary"
                    and func.ST_MakeArea(osm_tbl.c.geom).is_not(None),
                    func.St_BuildArea(osm_tbl.c.geom),
                ),
                else_=osm_tbl.c.geom,
            ).label("geom"),
        ]
    stmt = select(cols).select_from(osm_tbl).limit(limit)  # type: ignore
    if bbox:
        stmt = stmt.where(_in_bbox(osm_tbl.c.geom, bbox))  # type: ignore
    if query:
        stmt = stmt.where(osm_tbl.c.fts.op("@@")(func.websearch_to_tsquery(query)))
    return stmt


def sprel_query_stmt(
    *,
    location: Optional[str] = None,
    bbox: Optional[BBoxTuple] = None,
    relations: Optional[List[SpatialRelation]] = None,
    limit: Optional[int] = 10,
) -> Select:
    base: Select = get_osm_location(query=location, bbox=bbox)

    rel_ctes = []
    # # for each relation, create a CTE
    for i, rel in enumerate(relations or []):
        rel_stmt = get_osm_location(
            query=(rel.location.query if rel.location else None),
            bbox=(rel.location.bbox if rel.location else None) or bbox,
        )
        if rel.type == "covered_by":
            rel_stmt = rel_stmt.where(
                or_(
                    func.ST_GeometryType(osm_tbl.c.geom).in_(["ST_Polygon", "ST_MultiPolygon"]),
                    osm_tbl.c.category == "boundary",
                )
            )
        elif rel.type == "disjoint":
            rel_stmt = rel_stmt.where(
                func.ST_GeometryType(osm_tbl.c.geom).in_(
                    ["ST_Polygon", "ST_MultiPolygon", "ST_Line", "ST_MultiLine"]
                )
            )
        rel_ctes.append((rel, rel_stmt.cte(f"rel_{i}")))

    # # Make base a CTE after it has been modified
    base_cte = base.cte("base")
    # # Now start a join clause
    join_clause: Union[Join, CTE] = base_cte
    # # Now merge with the rel CTEs
    for i, (rel, cte) in enumerate(rel_ctes):
        if rel.type == "covered_by":
            join_clause = join_clause.join(cte, func.ST_CoveredBy(base_cte.c.geom, cte.c.geom))
        elif rel.type == "disjoint":
            join_clause = join_clause.join(cte, func.ST_Disjoint(base_cte.c.geom, cte.c.geom))
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
