"""OSM search functions."""
import logging
from functools import singledispatch
from typing import Any, Dict, List, Optional, Tuple, TypedDict, Union, cast

from fastapi import HTTPException
from geoalchemy2 import Geography, Geometry
from httpx import HTTPStatusError
from sqlalchemy import String, and_, or_
from sqlalchemy import cast as sql_cast
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import ColumnElement, Select

from app.core.config import get_settings
from app.core.datatypes import (
    BBox,
    Feature,
    FeatureCollection,
    Latitude,
    LineString,
    Longitude,
    MapProjection,
    Point,
)
from app.core.graphhopper import GraphHopper, get_graph_hopper
from app.db import osm as osm_tbl
from app.parsers.rules import (
    Buffer,
    Isochrone,
    NamedPlace,
    ParsedQuery,
    Place,
    Route,
    SpRelCoveredBy,
    SpRelDisjoint,
    SpRelNear,
    SpRelNotNear,
    SpRelOutsideDistOf,
    SpRelOutsideTimeOf,
    SpRelWithinDistOf,
    SpRelWithinTimeOf,
)

settings = get_settings()
graph_hopper = get_graph_hopper()

logger = logging.getLogger(__name__)

PLACE_STRING_SIMILARITY = 0.2
NAMED_PLACE_STRING_SIMILARITY = 0.2


def _in_bbox(
    col: ColumnElement,
    bbox: BBox,
    srid: int = MapProjection.WGS84,
) -> ColumnElement:
    """Return SQL expression check whether a geom is inside a bounding box."""
    envelope = func.ST_MakeEnvelope(*bbox, int(srid))
    return func.ST_Intersects(col, envelope)


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
            osm_tbl.c.tags,
        ]
    if include_geom:
        cols.append(osm_tbl.c.geom)
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
    arg: Place,  # pylint: disable=unused-argument
    bbox: Optional[BBox] = None,
    cols: Optional[List[ColumnElement]] = None,
) -> Select:
    """SQL query for Place.

    Returns results that match a full text search of the properties.

    """
    query = " ".join(arg.value)
    stmt = _select_osm(bbox=bbox, cols=cols).where(
        or_(osm_tbl.c.fts.op("@@")(func.plainto_tsquery(query)),
            func.similarity(query, osm_tbl.c.tags_text) > PLACE_STRING_SIMILARITY)
    )
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
        .where(or_(osm_tbl.c.fts.op("@@")(func.plainto_tsquery(query)),
                   func.similarity(query, osm_tbl.c.tags_text) > NAMED_PLACE_STRING_SIMILARITY))
        .order_by(func.ts_rank_cd(osm_tbl.c.fts, func.plainto_tsquery(query), 1).desc())
        .limit(limit)
    )
    return stmt


def _check_graph_hopper() -> None:
    if not graph_hopper:
        raise HTTPException(
            status_code=501,
            detail="GraphHopper is not configured, cannot generate isochrones",
        )


def _geocode(query: str, bbox: Optional[BBox] = None) -> Optional[Dict[str, Any]]:
    _check_graph_hopper()
    res = None
    try:
        res = cast(GraphHopper, graph_hopper).geocode(query, bbox=bbox, limit=1)
    except HTTPStatusError as exc:  # pylint: disable=broad-except
        logger.error("Error geocoding %s with Graphhopper: %s", query, exc)
    if res:
        hits = res.get("hits", [])
        if hits:
            return hits[0]
    # Note - results include a point and a bounding box, not the geom
    return None


def get_named_place_nominatim(query: str, bbox: Optional[BBox] = None) -> Optional[Select]:
    """Retrieve a named place using GraphHopper to geocode it."""
    # Since GraphHopper nominatinm returns a point and a bbox, we need to
    # lookup the goemetry in the OSM database. Returns none if no results.
    # TODO: raise exceptions
    _check_graph_hopper()
    res = _geocode(query, bbox=bbox)
    if res:
        osm_id = res.get("osm_id")
        if osm_id:
            stmt = _select_osm().where(osm_tbl.c.osm_id == osm_id)
            return stmt
    return None


@to_sql.register
def _(
    arg: NamedPlace, bbox: Optional[BBox] = None, **kwargs: Any  # pylint: disable=unused-argument
) -> Select:
    query = " ".join(arg.value)
    # hard code the case of San Francisco since we use it so much in early demos
    stmt = None
    if settings.graph_hopper.use_nominatim and graph_hopper:
        stmt = get_named_place_nominatim(query, bbox)
        if stmt is not None:
            return stmt
    return named_place_lookup_db(query=query, bbox=bbox)


@to_sql.register
def _(
    arg: SpRelCoveredBy, bbox: Optional[BBox] = None, limit: Optional[int] = None, offset: int = 0
) -> Select:
    subj = to_sql(arg.subject, bbox=bbox).cte()
    obj = (
        to_sql(arg.object, bbox=bbox, cols=[]).where(
            func.ST_GeometryType(osm_tbl.c.geom).in_(["ST_Polygon", "ST_MultiPolygon"])
        )
    ).cte()
    stmt = select(subj).join(obj, func.ST_CoveredBy(subj.c.geom, obj.c.geom))
    # Order by distance to the center of the object it is in
    stmt = stmt.order_by(
        func.ST_Distance(
            sql_cast(subj.c.geom, Geography()), sql_cast(func.ST_Centroid(obj.c.geom), Geography())
        )
    ).offset(offset)
    if limit:
        stmt = stmt.limit(limit)
    return stmt


@to_sql.register
def _(
    arg: SpRelDisjoint, bbox: Optional[BBox] = None, limit: Optional[int] = None, offset: int = 0
) -> Select:
    subj = to_sql(arg.subject, bbox=bbox).cte()
    obj = (
        to_sql(arg.object, bbox=bbox, cols=[])
        .where(
            func.ST_GeometryType(osm_tbl.c.geom).in_(["ST_Polygon", "ST_MultiPolygon"]),
        )
        .cte()
    )
    stmt = select(subj).join(obj, func.ST_Disjoint(subj.c.geom, obj.c.geom))
    # Order by distance to the object it is outside of, e.g. the closest objects that aren't inside that object
    # stmt = stmt.order_by(
    #     func.ST_Distance(sql_cast(subj.c.geom, Geography()), sql_cast(obj.c.geom, Geography()))
    # ).offset(offset)
    stmt = stmt.order_by().offset(offset)
    if limit:
        stmt = stmt.limit(limit)
    return stmt


@to_sql.register(SpRelWithinDistOf)
@to_sql.register(SpRelNear)
def _(
    arg: Union[SpRelNear, SpRelWithinDistOf],
    bbox: Optional[BBox] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = 0,
) -> Select:
    subj = to_sql(arg.subject, bbox=bbox).cte()
    obj = to_sql(arg.object, bbox=bbox, cols=[]).cte()
    stmt = select(subj).join(
        obj,
        and_(
            func.ST_Disjoint(subj.c.geom, obj.c.geom),
            func.ST_DWithin(
                sql_cast(subj.c.geom, Geography()), sql_cast(obj.c.geom, Geography()), arg.distance
            ),
        ),
    )

    stmt = stmt.order_by(
        func.ST_Distance(sql_cast(subj.c.geom, Geography()), sql_cast(obj.c.geom, Geography()))
    ).offset(offset)
    if limit:
        stmt = stmt.limit(limit)
    return stmt


@to_sql.register(SpRelOutsideDistOf)
@to_sql.register(SpRelNotNear)
def _(
    arg: Union[SpRelOutsideDistOf, SpRelNotNear],
    bbox: Optional[BBox] = None,
    limit: Optional[int] = None,
    offset: int = 0,
) -> Select:
    subj = to_sql(arg.subject, bbox=bbox).cte()
    obj = to_sql(arg.object, bbox=bbox, cols=[]).cte()
    stmt = select(subj).join(
        obj,
        # near or close to must be outside the object
        and_(
            func.ST_Disjoint(subj.c.geom, obj.c.geom),
            func.ST_Distance(sql_cast(subj.c.geom, Geography()), sql_cast(obj.c.geom, Geography()))
            > arg.distance,
        ),
    )
    # Order by the objects closest to the object it is not near
    stmt = stmt.order_by(
        func.ST_Distance(sql_cast(subj.c.geom, Geography()), sql_cast(obj.c.geom, Geography()))
    ).offset(offset)
    if limit:
        stmt = stmt.limit(limit)
    return stmt


@to_sql.register
def _(
    arg: Buffer, bbox: Optional[BBox] = None, limit: Optional[int] = None, offset: int = 0
) -> Select:
    obj = to_sql(arg.object, bbox=bbox, cols=[], limit=limit).cte()
    return (
        select(
            [
                obj.c.tags,
                obj.c.osm_type,
                obj.c.osm_id,
                sql_cast(
                    func.ST_Buffer(sql_cast(obj.c.geom, Geography()), arg.distance),
                    Geometry(srid=int(MapProjection.WGS84)),
                ).label("geom"),
            ]
        )
        .limit(limit)
        .offset(offset)
    )


def _feature_coll_sql(stmt: Select, limit: Optional[int] = None) -> Select:
    if limit:
        base = stmt.limit(limit)
    else:
        base = stmt
    base = select(
        func.to_geojson_feature(
            base.c.geom,
            func.jsonb_build_object(
                "osm",
                func.jsonb_build_object(
                    "tags", base.c.tags, "type", base.c.osm_type, "id", base.c.osm_id
                ),
            ),
            sql_cast(base.c.osm_id, String()),
        ).label("feature")
    )
    return base


def _get_isochrone(
    query: str, seconds: float, bbox: Optional[BBox] = None
) -> Tuple[Feature, Tuple[Latitude, Longitude]]:
    _check_graph_hopper()
    obj = _geocode(query, bbox=bbox)
    if not obj:
        raise ValueError("Could not geo-locate the named place")
    point: Dict[str, float] = obj["point"]
    res = cast(GraphHopper, graph_hopper).isochrone(
        (point["lat"], point["lng"]), int(seconds), profile="car"
    )
    return (
        Feature.parse_obj(res.get("polygons", [])[0]),
        (float(point["lat"]), float(point["lng"])),
    )


async def eval_isochrone(
    arg: Isochrone,
    bbox: Optional[BBox] = None,
) -> FeatureCollection:
    """Generate an isochrone from a center point and time in seconds.

    Currently hardcoded for cars.

    """
    _check_graph_hopper()
    if not isinstance(arg.object, NamedPlace):
        logger.warning("Attempting to search for an unnamed place")
    feature, _ = _get_isochrone(" ".join(arg.object.value), arg.duration.total_seconds(), bbox=bbox)
    return FeatureCollection(features=[feature])


async def eval_within_time_of(
    arg: SpRelWithinTimeOf,
    *,
    conn: AsyncConnection,
    bbox: Optional[BBox] = None,
    limit: Optional[int] = None,
    offset: int = 0,
) -> FeatureCollection:
    """Generate an isochrone from a center point and time in seconds.

    Currently hardcoded for cars.

    """
    _check_graph_hopper()
    if not isinstance(arg.object, NamedPlace):
        logger.warning("Attempting to search for an unnamed place")
    obj_poly, obj_point = _get_isochrone(
        " ".join(arg.object.value), arg.duration.total_seconds(), bbox=bbox
    )
    obj_lat, obj_lng = obj_point
    # Case: there is an isochrone, but no objects to check
    obj_geom = obj_poly.geometry.json()
    obj = select(
        [
            func.ST_GeomFromGeoJSON(obj_geom).label("geom"),
            func.ST_SetSRID(func.ST_MakePoint(obj_lng, obj_lat), int(MapProjection.WGS84)).label(
                "center"
            ),
        ]
    ).cte()
    subj = to_sql(arg.subject, bbox=bbox).cte()
    if subj is None:
        return FeatureCollection(features=[])
    # TODO: any subject features should also be outside of the starting point of the
    # isochrone.
    stmt = (
        select(subj)
        .join(
            obj,
            and_(
                func.ST_Intersects(subj.c.geom, obj.c.geom),
                func.ST_Disjoint(subj.c.geom, obj.c.center),
            ),
        )
        .order_by(func.ST_Distance(subj.c.geom, obj.c.center))
    ).offset(offset)
    if limit:
        stmt = stmt.limit(limit)
    res = await conn.execute(_feature_coll_sql(stmt))
    return FeatureCollection(features=[r.feature for r in res])


async def eval_outside_time_of(
    arg: SpRelOutsideTimeOf,
    *,
    conn: AsyncConnection,
    bbox: Optional[BBox] = None,
    limit: Optional[int] = None,
    offset: int = 0,
) -> FeatureCollection:
    """Generate an isochrone from a center point and time in seconds.

    Currently hardcoded for cars.

    """
    # get feature collection from isochrone
    _check_graph_hopper()
    if not isinstance(arg.object, NamedPlace):
        logger.warning("Attempting to search for an unnamed place")
    obj_poly, obj_point = _get_isochrone(
        " ".join(arg.object.value), arg.duration.total_seconds(), bbox=bbox
    )
    obj_lat, obj_lng = obj_point
    # Case: there is an isochrone, but no objects to check
    obj_geom = obj_poly.geometry.json()
    obj = select(
        [
            func.ST_GeomFromGeoJSON(obj_geom).label("geom"),
            func.ST_SetSRID(func.ST_MakePoint(obj_lng, obj_lat), int(MapProjection.WGS84)).label(
                "center"
            ),
        ]
    ).cte()
    subj = to_sql(arg.subject, bbox=bbox).cte()
    if subj is None:
        return FeatureCollection(features=[])
    # TODO: any subject features should also be outside of the starting point of the
    # isochrone.
    stmt = (
        select(subj)
        .join(obj, func.ST_Disjoint(subj.c.geom, obj.c.geom))
        .order_by(func.ST_Distance(subj.c.geom, obj.c.center))
    ).offset(offset)
    if limit:
        stmt = stmt.limit(limit)
    res = (await conn.execute(_feature_coll_sql(stmt))).scalar()
    return FeatureCollection.parse_obj(res or {})


class _PointDict(TypedDict):
    lat: float
    lng: float


async def eval_route(arg: Route, *, bbox: Optional[BBox] = None) -> FeatureCollection:
    """Generate a route from a start point to an end point."""
    # lat, lon = 37.7749, -122.4194
    _check_graph_hopper()
    start = _geocode(" ".join(arg.start.value), bbox=bbox)
    if not start:
        raise ValueError(f"Could not geo-locate the start point {arg.start}")
    start_point: _PointDict = start["point"]
    end = _geocode(" ".join(arg.end.value), bbox=bbox)
    if not end:
        raise ValueError(f"Could not geo-locate the end point {arg.end}")
    end_point: _PointDict = end["point"]
    res = cast(GraphHopper, graph_hopper).route(
        (start_point["lat"], start_point["lng"]), (end_point["lat"], end_point["lng"])
    )
    points = LineString.parse_obj(res["paths"][0]["points"])
    return FeatureCollection(
        features=[
            Feature(geometry=points, properties={"name": "route"}),
            Feature(
                geometry=Point(coordinates=[start_point["lng"], start_point["lat"]]),
                properties={"name": "start"},
            ),
            Feature(
                geometry=Point(coordinates=[end_point["lng"], end_point["lat"]]),
                properties={"name": "end"},
            ),
        ]
    )


async def eval_query(
    arg: ParsedQuery,
    *,
    conn: AsyncConnection,
    bbox: Optional[BBox] = None,
    limit: Optional[int] = None,
    offset: int = 0,
) -> FeatureCollection:
    """Evaluate a query"""
    expr = arg.value
    if isinstance(expr, Isochrone):
        return await eval_isochrone(expr, bbox=bbox)
    if isinstance(expr, SpRelWithinTimeOf):
        return await eval_within_time_of(expr, bbox=bbox, conn=conn, offset=offset)
    if isinstance(expr, SpRelOutsideTimeOf):
        return await eval_outside_time_of(expr, bbox=bbox, conn=conn, offset=offset)
    if isinstance(expr, Route):
        return await eval_route(expr, bbox=bbox)
    stmt = _feature_coll_sql(to_sql(expr, bbox=bbox, limit=limit, offset=offset))
    res = await conn.execute(stmt)
    features = [r.feature for r in res]
    return FeatureCollection(features=features)
