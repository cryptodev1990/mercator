"""CRUD functions for interacting with shapes.

NOTE: All queries use `shapes` table and no ORM features
"""
import datetime
import logging
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Union, cast

import jinja2
import sqlalchemy as sa
from geojson_pydantic import Feature, LineString, Point, Polygon
from pydantic import UUID4
from sqlalchemy.engine import Connection

from app import schemas
from app.db.metadata import shapes as shapes_tbl

logger = logging.getLogger(__name__)


class MapProjection(str, Enum):
    WGS84 = 4326
    WEB_MERCATOR = 3857


DEFAULT_LIMIT = 25
METADATA_COLS = [
    shapes_tbl.c.uuid,
    shapes_tbl.c.name,
    shapes_tbl.c.properties,
    shapes_tbl.c.created_at,
    shapes_tbl.c.updated_at,
]


def get_shape(conn: Connection, shape_id: UUID4) -> Optional[schemas.GeoShape]:
    """Get a shape."""
    query = (
        shapes_tbl.select()
        .where(shapes_tbl.c.deleted_at == None)
        .where(shapes_tbl.c.uuid == shape_id)
        .limit(1)
    )
    res = conn.execute(query).first()
    if res:
        return schemas.GeoShape.from_orm(res)
    return None


def get_all_shapes_by_user(
    conn: Connection,
    user_id: int,
    limit: Optional[int] = DEFAULT_LIMIT,
    offset: int = 0,
) -> List[schemas.GeoShape]:
    """Get all shapes created by a user."""
    # TODO ordering by UUID just guarantees a sort order
    # I am only doing this because the selected feature index in nebula.gl
    # on the frontend needs consistent
    # We should find a better way of handling this
    stmt = (
        shapes_tbl.select()
        .where(shapes_tbl.c.created_by_user_id == user_id)
        .where(shapes_tbl.c.deleted_at == None)
        .order_by(shapes_tbl.c.uuid)
        .offset(offset)
    )
    if limit is not None:
        stmt = stmt.limit(limit)
    res = conn.execute(stmt).fetchall()
    return [schemas.GeoShape.from_orm(g) for g in list(res)]


def get_shape_metadata_by_bounding_box(
    conn: Connection,
    bbox: schemas.ViewportBounds,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> List[schemas.GeoShapeMetadata]:
    """Get all shapes within a bounding box

    Used on the frontend to determine which shapes to show details on in the sidebar
    """
    geom = Polygon(
        type="Polygon",
        coordinates=[
            [
                (bbox.min_x, bbox.min_y),
                (bbox.min_x, bbox.max_y),
                (bbox.max_x, bbox.max_y),
                (bbox.max_x, bbox.min_y),
                (bbox.min_x, bbox.min_y),
            ]
        ],
    )
    stmt = (
        sa.select(shapes_tbl)  # type: ignore
        .with_only_columns(METADATA_COLS)
        .where(shapes_tbl.c.deleted_at == None)
        .where(
            # Check if the shape intersects with the bounding box
            sa.func.ST_Intersects(
                shapes_tbl.c.geom,
                sa.func.ST_GeomFromText(
                    geom.wkt,
                    4326,
                ),
            )
        )
        .order_by(shapes_tbl.c.uuid)
        .limit(limit)
        .offset(offset)
    )

    res = conn.execute(stmt).fetchall()
    return [schemas.GeoShapeMetadata.from_orm(g) for g in list(res)]


def get_shape_metadata_matching_search(
    conn: Connection, search_query: str, limit: int = DEFAULT_LIMIT, offset: int = 0
) -> List[schemas.GeoShapeMetadata]:
    """Get all shapes matching a search string."""
    stmt = sa.text(
        """
        SELECT uuid
        , name
        , properties - '__uuid' AS properties
        , created_at
        , updated_at
        , ts_rank_cd(fts, query, 12) AS rank
        FROM shapes
        , websearch_to_tsquery(:query_text) query
        , SIMILARITY(:query_text, properties::VARCHAR) similarity
        WHERE 1=1
          AND (query @@ fts OR similarity > 0)
        ORDER BY rank DESC, similarity DESC
        LIMIT :limit
        OFFSET :offset
    """
    )
    res = conn.execute(
        stmt, {"query_text": search_query, "limit": limit, "offset": offset}
    ).fetchall()
    return [schemas.GeoShapeMetadata.from_orm(g) for g in list(res)]


def get_all_shape_metadata_by_organization(
    conn: Connection,
    organization_id: UUID4,
    limit: Optional[int] = DEFAULT_LIMIT,
    offset: int = 0,
) -> List[schemas.GeoShapeMetadata]:
    # TODO remove UUID ordering
    stmt = (
        shapes_tbl.select()
        .with_only_columns(METADATA_COLS)
        # type: ignore
        .where(shapes_tbl.c.organization_id == str(organization_id))
        .where(shapes_tbl.c.deleted_at == None)
        .order_by(shapes_tbl.c.uuid)
        .offset(offset)
        .limit(limit)
    )
    res = conn.execute(stmt).fetchall()
    return [schemas.GeoShapeMetadata.from_orm(g) for g in list(res)]


def get_all_shapes_by_organization(
    conn: Connection,
    organization_id: UUID4,
    limit: Optional[int] = DEFAULT_LIMIT,
    offset: int = 0,
) -> List[schemas.GeoShape]:
    # TODO Remove ordering by UUID
    stmt = (
        shapes_tbl.select()
        .where(shapes_tbl.c.organization_id == str(organization_id))
        .where(shapes_tbl.c.deleted_at == None)
        .order_by(shapes_tbl.c.uuid)
        .limit(limit)
        .offset(offset)
    )
    res = conn.execute(stmt).fetchall()
    return [schemas.GeoShape.from_orm(g) for g in list(res)]


def _process_geojson(geojson: Feature, name: Optional[str] = None) -> Dict[str, Any]:
    if geojson.properties is None:
        geojson.properties = {}
    if name:
        geojson.properties["name"] = name
    if geojson.properties["name"] is None:
        geojson.properties["name"] = "New shape"
    return {"geojson": geojson.dict(), "name": geojson.properties["name"]}


def create_shape(
    conn: Connection, geoshape: schemas.GeoShapeCreate
) -> schemas.GeoShape:
    """Create a new shape."""

    ins = (
        shapes_tbl.insert()
        .values(
            created_by_user_id=sa.func.app_user_id(),
            updated_by_user_id=sa.func.app_user_id(),
            updated_at=sa.func.now(),
            created_at=sa.func.now(),
            organization_id=sa.func.app_user_org(),
            **_process_geojson(geoshape.geojson, geoshape.name),
        )
        .returning(shapes_tbl)  # type: ignore
    )
    res = conn.execute(ins).first()
    if res is None:
        raise Exception("No rows updated")
    shape: Dict[str, Any] = dict(res)
    shape["properties"] = cast(Dict[str, Any], shape.get("geojson")).get(
        "properties", {}
    )
    shape["name"] = cast(Dict[str, Any], shape).get("properties", {}).get("name")
    return schemas.GeoShape.parse_obj(shape)


def create_many_shapes(
    conn: Connection, geoshapes: Sequence[schemas.GeoShapeCreate]
) -> List[UUID4]:
    """Create many new shapes."""
    ins = (
        shapes_tbl.insert()
        .values(
            created_by_user_id=sa.func.app_user_id(),
            created_at=sa.func.now(),
            updated_by_user_id=sa.func.app_user_id(),
            updated_at=sa.func.now(),
            organization_id=sa.func.app_user_org(),
        )
        .returning(shapes_tbl.c.uuid)
    )
    new_shapes = conn.execute(
        ins, [_process_geojson(s.geojson, s.name) for s in geoshapes]
    ).scalars()
    return list(new_shapes)


def update_shape(
    conn: Connection, geoshape: schemas.GeoShapeUpdate
) -> schemas.GeoShape:
    """Update a shape with additional information."""
    values = {
        "name": geoshape.name,
        "updated_at": datetime.datetime.now(),
        "updated_by_user_id": sa.func.app_user_id(),
    }
    if geoshape.geojson:
        values["geojson"] = geoshape.geojson.dict()
    update_stmt = (
        shapes_tbl.update()
        .values(**values)
        .where(shapes_tbl.c.uuid == str(geoshape.uuid))
        .returning(shapes_tbl)
    )
    res = conn.execute(update_stmt).first()
    if res is None:
        raise Exception("No rows updated")
    shape: Dict[str, Any] = dict(res)
    shape["properties"] = cast(Dict[str, Any], shape.get("geojson")).get(
        "properties", {}
    )
    shape["name"] = cast(Dict[str, Any], shape).get("properties", {}).get("name")
    return schemas.GeoShape.parse_obj(shape)


def delete_shape(conn: Connection, uuid: UUID4) -> int:
    """Delete a shape."""
    # TODO: What to do if exists?
    values = {
        "deleted_at": datetime.datetime.now(),
        "deleted_by_user_id": sa.func.app_user_id(),
    }
    stmt = (
        shapes_tbl.update()
        .values(**values)
        .where(shapes_tbl.c.uuid == str(uuid))
        .returning(shapes_tbl.c.uuid)  # type: ignore
    )
    res = conn.execute(stmt)
    rows = res.rowcount
    return rows


def delete_many_shapes(conn: Connection, uuids: Sequence[UUID4]) -> int:
    """Delete many shapes."""
    # TODO: What to do if exists?
    values = {
        "deleted_at": datetime.datetime.now(),
        "deleted_by_user_id": sa.func.app_user_id(),
    }
    stmt = (
        shapes_tbl.update()
        .values(**values)
        .where(shapes_tbl.c.uuid.in_(tuple([str(x) for x in uuids])))
    )  # type: ignore
    res = conn.execute(stmt)
    rows = res.rowcount
    return rows


def get_shape_count(conn: Connection) -> int:
    """Get the number of shapes in an organization."""
    stmt = (
        sa.select(sa.func.count(shapes_tbl.c.uuid))
        .where(shapes_tbl.c.organization_id == sa.func.app_user_org())
        .where(shapes_tbl.c.deleted_at == None)
    )
    res = conn.execute(stmt).fetchone()
    return res[0]


def get_shapes_containing_point(
    conn: Connection, lat: float, lng: float
) -> List[Feature]:
    """Get the shape that contains a point."""
    stmt = sa.text(
        """
    SELECT *
    FROM shapes
    WHERE 1=1
      AND ST_Contains(geom, ST_GeomFromText('POINT(:lng :lat)', 4326))
      AND deleted_at IS NULL
      AND organization_id = public.app_user_org()
    """
    )
    res = conn.execute(stmt, {"lat": lat, "lng": lng}).fetchall()
    if res:
        return [schemas.GeoShape.from_orm(row).geojson for row in res]
    return []


class GeometryOperation(str, Enum):
    """Valid geometry operations."""

    contains = "contains"
    intersects = "intersects"
    touches = "touches"
    crosses = "crosses"


def get_shapes_related_to_geom(
    conn: Connection,
    operation: GeometryOperation,
    geom: Union[Point, Polygon, LineString],
) -> List[Feature]:
    """Get the shape that contains a point."""
    stmt = sa.text(
        jinja2.Template(
            """
    SELECT *
    FROM shapes
    WHERE 1=1
      AND ST_{{operation}}(geom, ST_GeomFromGeoJSON(:geom))
      AND deleted_at IS NULL
      AND organization_id = public.app_user_org()
    """
        ).render(operation=operation.title())
    )
    res = conn.execute(stmt, {"geom": geom.json()}).fetchall()
    if res:
        return [schemas.GeoShape.from_orm(row).geojson for row in res]
    return []
