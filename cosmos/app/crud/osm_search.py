"""OSM search functions."""
import logging
from functools import singledispatch
from typing import Any, List, Optional, Union

from geoalchemy2 import Geography, Geometry
from sqlalchemy import String, and_
from sqlalchemy import case as sql_case
from sqlalchemy import cast, func, or_, select
from sqlalchemy.sql import ColumnElement, Select

from app.core.datatypes import BBox, MapProjection
from app.db import osm as osm_tbl
from app.parsers.rules import (
    Buffer,
    NamedPlace,
    ParsedQuery,
    Place,
    SpRelCoveredBy,
    SpRelDisjoint,
    SpRelNear,
    SpRelNotNear,
    SpRelWithinDistOf,
    SpRelOutsideDistOf
)

logger = logging.getLogger(__name__)


def _in_bbox(
    col: ColumnElement,
    bbox: BBox,
    srid: int = MapProjection.WGS84,
) -> ColumnElement:
    """Return SQL expression check whether a geom is inside a bounding box."""
    envelope = func.ST_MakeEnvelope(*bbox, int(srid))
    return func.ST_Intersects(col, envelope)


# Returns osm features
def search_osm(
    *,
    query: Optional[str] = None,
    bbox: Optional[BBox] = None,
    osm_id: Optional[str] = None,
    limit: Optional[int] = None,
    cols: Optional[List[ColumnElement[Any]]] = None,
) -> Select:
    """Generate a select statement for the OSM database."""
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
    if osm_id:
        stmt = stmt.where(cast(osm_tbl.c.osm_id, String()) == osm_id) # type: ignore
    if query:
        stmt = stmt.where(osm_tbl.c.fts.op("@@")(func.websearch_to_tsquery(query)))
    return stmt


@singledispatch
def to_sql(arg: Any, **kwargs: Any) -> Any:
    """Convert a parsed query to a SQL statement."""
    raise NotImplementedError(f"Cannot convert {arg} to SQL")


@to_sql.register
def _(arg: Place, bbox: Optional[BBox] = None) -> Select:
    query = " ".join(arg.value)
    return search_osm(query=query, bbox=bbox)


@to_sql.register
def _(arg: NamedPlace, bbox: Optional[BBox] = None) -> Select:
    query = " ".join(arg.value)
    # hard code the case of San Francisco since we use it so much in early demos
    if query.lower() == "san francisco":
        return search_osm(osm_id="111968")
    return search_osm(query=query, bbox=bbox)


@to_sql.register
def _(arg: SpRelCoveredBy, bbox: Optional[BBox] = None) -> Select:
    subj = to_sql(arg.subject, bbox=bbox).cte()
    obj = (
        to_sql(arg.object, bbox=bbox).where(
            or_(
                func.ST_GeometryType(osm_tbl.c.geom).in_(["ST_Polygon", "ST_MultiPolygon"]),
                osm_tbl.c.category == "boundary",
            )
        )
    ).cte()
    join_clause = select(subj).join(obj, func.ST_CoveredBy(subj.c.geom, obj.c.geom))
    return join_clause

@to_sql.register
def _(arg: SpRelDisjoint, bbox: Optional[BBox] = None) -> Select:
    subj = to_sql(arg.subject, bbox=bbox).cte()
    obj = (
        to_sql(arg.object, bbox=bbox)
        .where(
            or_(
                func.ST_GeometryType(osm_tbl.c.geom).in_(["ST_Polygon", "ST_MultiPolygon"]),
                osm_tbl.c.category == "boundary",
            )
        )
        .cte()
    )

    join_clause = select(subj).join(obj, func.ST_Disjoint(subj.c.geom, obj.c.geom))
    return join_clause


@to_sql.register(SpRelOutsideDistOf)
@to_sql.register(SpRelNotNear)
def _(arg: Union[SpRelOutsideDistOf, SpRelNotNear], bbox: Optional[BBox] = None) -> Select:
    subj = to_sql(arg.subject, bbox=bbox).cte()
    obj = to_sql(arg.object, bbox=bbox).cte()
    join_clause = select(subj).join(
        obj,
        and_(
            func.ST_Disjoint(subj.c.geom, obj.c.geom),
            func.ST_Distance(cast(subj.c.geom, Geography()), cast(obj.c.geom, Geography()))
            > arg.distance,
        ),
    )
    return join_clause


@to_sql.register(SpRelWithinDistOf)
@to_sql.register(SpRelNear)
def _(arg: Union[SpRelNear, SpRelWithinDistOf], bbox: Optional[BBox] = None) -> Select:
    subj = to_sql(arg.subject, bbox=bbox).cte()
    obj = to_sql(arg.object, bbox=bbox).cte()
    join_clause = select(subj).join(
        obj,
        and_(
            func.ST_Disjoint(subj.c.geom, obj.c.geom),
            func.ST_DWithin(
                cast(subj.c.geom, Geography()), cast(obj.c.geom, Geography()), arg.distance
            ),
        ),
    )
    return join_clause


@to_sql.register
def _(arg: Buffer, bbox: Optional[BBox] = None) -> Select:
    obj = to_sql(arg.object, bbox=bbox).cte()
    return select(
        [
            obj.c.tags,
            obj.c.osm_type,
            obj.c.osm_id,
            obj.c.category,
            cast(
                func.ST_Buffer(cast(obj.c.geom, Geography()), arg.distance),
                Geometry(srid=MapProjection.WGS84),
            ).label("geom"),
        ]
    )


@to_sql.register
def _(arg: ParsedQuery, bbox: Optional[BBox] = None, limit: Optional[int] = None) -> Select:
    base = to_sql(arg.value, bbox=bbox).cte()
    stmt = (
        select(
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
        .select_from(base)
        .limit(limit)
    )
    return stmt
