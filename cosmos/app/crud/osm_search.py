"""OSM search functions."""
import logging
from functools import singledispatch
from typing import Any, List, Optional, Union

from geoalchemy2 import Geography, Geometry
from httpx import HTTPStatusError
from sqlalchemy import String, Table, and_
from sqlalchemy import case as sql_case
from sqlalchemy import cast, func, or_, select
from sqlalchemy.sql import ColumnElement, Select

from app.core.config import get_settings
from app.core.datatypes import BBox, MapProjection
from app.core.graphhopper import get_graph_hopper
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
    SpRelOutsideDistOf,
    SpRelWithinDistOf,
)

settings = get_settings()
graph_hopper = get_graph_hopper()

logger = logging.getLogger(__name__)


def _in_bbox(
    col: ColumnElement,
    bbox: BBox,
    srid: int = MapProjection.WGS84,
) -> ColumnElement:
    """Return SQL expression check whether a geom is inside a bounding box."""
    envelope = func.ST_MakeEnvelope(*bbox, int(srid))
    return func.ST_Intersects(col, envelope)


def _geom_col(tbl: Table) -> ColumnElement:
    return sql_case(
        (
            tbl.c.category == "boundary" and func.ST_MakeArea(tbl.c.geom).is_not(None),
            func.St_BuildArea(tbl.c.geom),
        ),
        else_=tbl.c.geom,
    )


def _select_osm(
    *,
    bbox: Optional[BBox] = None,
    limit: Optional[int] = None,
    include_geom: bool = True,
    cols: Optional[List[ColumnElement[Any]]] = None,
) -> Select:
    """Reusable select statement for the OSM database."""
    if cols is None:
        cols = [
            osm_tbl.c.osm_id,
            osm_tbl.c.osm_type,
            osm_tbl.c.category,
            osm_tbl.c.tags,
        ]
    if include_geom:
        cols.append(_geom_col(osm_tbl).label("geom"))
    stmt = select(cols).select_from(osm_tbl)  # type: ignore
    if bbox:
        stmt = stmt.where(_in_bbox(osm_tbl.c.geom, bbox))  # type: ignore
    if limit:
        stmt = stmt.limit(limit)
    return stmt


@singledispatch
def to_sql(arg: Any, **kwargs: Any) -> Any:
    """Convert a parsed query to a SQL statement."""
    raise NotImplementedError(f"Cannot convert {arg} to SQL")


@to_sql.register
def _(
    arg: Place, bbox: Optional[BBox] = None, **kwargs: Any  # pylint: disable=unused-argument
) -> Select:
    """SQL query for Place.

    Returns results that match a full text search of the properties.

    """
    query = " ".join(arg.value)
    stmt = _select_osm(bbox=bbox).where(osm_tbl.c.fts.op("@@")(func.plainto_tsquery(query)))
    return stmt


def named_place_lookup_db(
    query: str,
    bbox: Optional[BBox] = None,
    limit: int = 1,
    cols: Optional[List[ColumnElement]] = None,
) -> Select:
    """Search OSM for a place.

    Uses FTS to search for a place name, and returns the OSM ID of the first
    results sorted by `ts_rank_cd`.

    """
    stmt = (
        _select_osm(bbox=bbox, cols=cols)
        .where(osm_tbl.c.fts.op("@@")(func.plainto_tsquery(query)))
        .order_by(func.ts_rank_cd(osm_tbl.c.fts, func.plainto_tsquery(query), 1).desc())
        .limit(limit)
    )
    return stmt


@to_sql.register
def _(
    arg: NamedPlace, bbox: Optional[BBox] = None, **kwargs: Any  # pylint: disable=unused-argument
) -> Select:
    query = " ".join(arg.value)
    # hard code the case of San Francisco since we use it so much in early demos
    if settings.graph_hopper.use_nominatim and graph_hopper:
        res = None
        try:
            logger.exception("Querying GraphHopper for %s", query)
            res = graph_hopper.geocode(" ".join(arg.value), bbox=bbox, limit=1)
        except HTTPStatusError as exc:  # pylint: disable=broad-except
            logger.error("Error geocoding %s with Graphhopper: %s", arg.value, exc)
        osm_id = None
        if res:
            hits = res.get("hits", [])
            if not hits:
                logger.debug("No geocode results found for Graphhopper: %s")
            else:
                osm_id = hits[0].get("osm_id")
        if osm_id:
            return _select_osm().where(osm_tbl.c.osm_id == osm_id)
    return named_place_lookup_db(query=query, bbox=bbox)


@to_sql.register
def _(arg: SpRelCoveredBy, bbox: Optional[BBox] = None, limit: Optional[int] = None) -> Select:
    subj = to_sql(arg.subject, bbox=bbox).cte()
    obj = (
        to_sql(arg.object, bbox=bbox).where(
            or_(
                func.ST_GeometryType(osm_tbl.c.geom).in_(["ST_Polygon", "ST_MultiPolygon"]),
                osm_tbl.c.category == "boundary",
            )
        )
    ).cte()
    stmt = select(subj).join(obj, func.ST_CoveredBy(subj.c.geom, obj.c.geom))
    # Order by distance to the center of the object it is in
    stmt = stmt.order_by(
        func.ST_Distance(
            cast(subj.c.geom, Geography()), cast(func.ST_Centroid(obj.c.geom), Geography())
        )
    )
    if limit:
        stmt = stmt.limit(limit)
    return stmt


@to_sql.register
def _(arg: SpRelDisjoint, bbox: Optional[BBox] = None, limit: Optional[int] = None) -> Select:
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
    stmt = select(subj).join(obj, func.ST_Disjoint(subj.c.geom, obj.c.geom))
    # Order by distance to the object it is outside of, e.g. the closest objects that aren't inside that object
    stmt = stmt.order_by(
        func.ST_Distance(cast(subj.c.geom, Geography()), cast(obj.c.geom, Geography()))
    )
    if limit:
        stmt = stmt.limit(limit)
    return stmt


@to_sql.register(SpRelWithinDistOf)
@to_sql.register(SpRelNear)
def _(
    arg: Union[SpRelNear, SpRelWithinDistOf],
    bbox: Optional[BBox] = None,
    limit: Optional[int] = None,
) -> Select:
    subj = to_sql(arg.subject, bbox=bbox).cte()
    obj = to_sql(arg.object, bbox=bbox).cte()
    stmt = select(subj).join(
        obj,
        and_(
            func.ST_Disjoint(subj.c.geom, obj.c.geom),
            func.ST_DWithin(
                cast(subj.c.geom, Geography()), cast(obj.c.geom, Geography()), arg.distance
            ),
        ),
    )
    if limit:
        stmt = stmt.limit(limit)
    stmt = stmt.order_by(
        func.ST_Distance(cast(subj.c.geom, Geography()), cast(obj.c.geom, Geography()))
    )
    return stmt


@to_sql.register(SpRelOutsideDistOf)
@to_sql.register(SpRelNotNear)
def _(
    arg: Union[SpRelOutsideDistOf, SpRelNotNear],
    bbox: Optional[BBox] = None,
    limit: Optional[int] = None,
) -> Select:
    subj = to_sql(arg.subject, bbox=bbox).cte()
    obj = to_sql(arg.object, bbox=bbox).cte()
    stmt = select(subj).join(
        obj,
        and_(
            func.ST_Disjoint(subj.c.geom, obj.c.geom),
            func.ST_Distance(cast(subj.c.geom, Geography()), cast(obj.c.geom, Geography()))
            > arg.distance,
        ),
    )
    # Order by the objects closest to the object it is not near
    stmt = stmt.order_by(
        func.ST_Distance(cast(subj.c.geom, Geography()), cast(obj.c.geom, Geography()))
    )
    if limit:
        stmt = stmt.limit(limit)
    return stmt


@to_sql.register
def _(arg: Buffer, bbox: Optional[BBox] = None, limit: Optional[int] = None) -> Select:
    obj = to_sql(arg.object, bbox=bbox, limit=limit).cte()
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
    ).limit(limit)


@to_sql.register
def _(arg: ParsedQuery, bbox: Optional[BBox] = None, limit: Optional[int] = None) -> Select:
    base = to_sql(arg.value, bbox=bbox, limit=limit).cte()
    stmt = select(
        func.to_geojson_feature_collection_agg(
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
        ).label("features")
    ).select_from(base)
    return stmt
