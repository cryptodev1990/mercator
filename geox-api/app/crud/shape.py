"""CRUD functions for interacting with shapes.

NOTE: All queries use `shapes` table and no ORM features
"""
import datetime
import logging
from enum import Enum
from typing import Any, Dict, Generator, List, Optional, Sequence, Union

import jinja2
import sqlalchemy as sa
from geojson_pydantic import Feature, Polygon, Point, LineString
from pydantic import UUID4
from sqlalchemy import insert, select, update, func  # type: ignore
from sqlalchemy.engine import Connection

from app.crud.namespaces import NamespaceDoesNotExistError, get_default_namespace
from app.db.metadata import shapes as shapes_tbl
from app.schemas import GeoShape, GeoShapeCreate, GeoShapeMetadata, ViewportBounds

logger = logging.getLogger(__name__)


class MapProjection(str, Enum):
    WGS84 = 4326
    WEB_MERCATOR = 3857


METADATA_COLS = [
    shapes_tbl.c.uuid,
    shapes_tbl.c.name,
    shapes_tbl.c.namespace_id,
    shapes_tbl.c.properties,
    shapes_tbl.c.created_at,
    shapes_tbl.c.updated_at,
]

## Read Shapes


class ShapeDoesNotExist(Exception):
    def __init__(self, id_: UUID4) -> None:
        self.id = id_

    def __str__(self) -> str:
        return f"Shape {self.id} does not exist."


## Create Shapes


def create_shape(
    conn: Connection,
    *,
    user_id: int,
    geojson: Feature,
    organization_id: UUID4,
    name: Optional[str] = None,
    namespace_id: Optional[UUID4] = None,
) -> GeoShape:
    """Create a new shape."""
    if namespace_id is None:
        # TODO: remove this once namespaces are migrated
        namespace_id = get_default_namespace(conn, organization_id).id
    if geojson.properties is None:
        geojson.properties = {}
    if name:
        geojson.properties["name"] = name
    # The trigger that updates properties from geojson does not run until
    # after returning retrieves values for the row. the following lines
    # work around that
    stmt = insert(shapes_tbl).returning(
        shapes_tbl.c.uuid,
        shapes_tbl.c.created_at,
        shapes_tbl.c.updated_at,
        shapes_tbl.c.geojson,
        shapes_tbl.c.namespace_id,
    )  # type: ignore
    values = {
        "created_by_user_id": user_id,
        "updated_by_user_id": user_id,
        "organization_id": organization_id,
        "geojson": geojson.dict(),
        "namespace_id": namespace_id,
    }
    res = conn.execute(stmt, values).first()
    new_shape = dict(res)
    new_shape["name"] = new_shape["geojson"].get("properties", {}).get("name")
    new_shape["properties"] = new_shape["geojson"].get("properties", {})
    return GeoShape.parse_obj(dict(new_shape))


def _process_geojson(geojson: Feature, name: Optional[str] = None) -> Dict[str, Any]:
    if geojson.properties is None:
        geojson.properties = {}
    if name:
        geojson.properties["name"] = name
    return {"geojson": geojson.dict(), "name": geojson.properties["name"]}


def create_many_shapes(
    conn: Connection,
    data: Sequence[GeoShapeCreate],
    user_id: int,
    organization_id: UUID4,
    namespace_id: Optional[UUID4] = None,
) -> Generator[UUID4, None, None]:
    """Create many new shapes."""
    stmt = (
        insert(shapes_tbl)  # type: ignore
        .values(
            created_by_user_id=user_id,
            updated_by_user_id=user_id,
            organization_id=organization_id,
        )
        .returning(shapes_tbl.c.uuid)
    )
    ## TODO: remove exception after migration
    default_namespace = namespace_id or get_default_namespace(conn, organization_id).id
    values = [
        {
            **_process_geojson(x.geojson, x.name),
            "namespace_id": x.namespace or default_namespace,
        }
        for x in data
    ]
    new_shapes = conn.execute(stmt, values)
    for row in new_shapes:
        yield row.uuid


def get_shape(conn: Connection, shape_id: UUID4) -> GeoShape:
    """Get a shape."""
    stmt = (
        select(shapes_tbl)  # type: ignore
        .where(shapes_tbl.c.deleted_at.is_(None))
        .where(shapes_tbl.c.uuid == str(shape_id))
        .limit(1)
    )
    res = conn.execute(stmt).first()
    if res is None:
        raise ShapeDoesNotExist(shape_id)
    return GeoShape.parse_obj(dict(res))


def select_shapes(
    conn: Connection,
    *,
    user_id: Optional[int] = None,
    organization_id: Optional[UUID4] = None,
    namespace_id: Optional[UUID4] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = 0,
) -> Generator[GeoShape, None, None]:
    # This will be called many times - use more advanced caching
    stmt = select(shapes_tbl).where(shapes_tbl.c.deleted_at.is_(None)).order_by(shapes_tbl.c.uuid)  # type: ignore
    if user_id is not None:
        stmt = stmt.where(shapes_tbl.c.created_by_user_id == user_id)
    if namespace_id is not None:
        stmt = stmt.where(shapes_tbl.c.namespace_id == namespace_id)
    if organization_id is not None:
        stmt = stmt.where(shapes_tbl.c.organization_id == organization_id)
    if offset is not None:
        stmt = stmt.offset(offset)
    if limit:
        stmt = stmt.limit(limit)
    res = conn.execute(stmt)
    for row in res:
        print(row)
        yield GeoShape.parse_obj(dict(row))


def get_all_shapes_by_user(
    conn: Connection,
    user_id: int,
    limit: Optional[int] = None,
    offset: int = 0,
) -> List[GeoShape]:
    """Get all shapes created by a user."""
    return list(select_shapes(conn, user_id=user_id, limit=limit, offset=offset))


def get_all_shapes_by_organization(
    conn: Connection,
    user_id: int,
    limit: Optional[int] = None,
    offset: int = 0,
) -> List[GeoShape]:
    """Get all shapes created by a user."""
    return list(select_shapes(conn, user_id=user_id, limit=limit, offset=offset))


def select_shape_metadata(
    conn: Connection,
    *,
    user_id: Optional[int] = None,
    organization_id: Optional[UUID4] = None,
    namespace_id: Optional[UUID4] = None,
    limit: Optional[int] = None,
    offset: int = 0,
) -> Generator[GeoShapeMetadata, None, None]:
    """Query shape metadata."""
    # This will be called many times - use more advanced caching
    stmt = select(shapes_tbl).with_only_columns(METADATA_COLS).where(shapes_tbl.c.deleted_at.is_(None)).order_by(shapes_tbl.c.uuid).offset(offset).limit(limit)  # type: ignore
    if user_id is not None:
        stmt = stmt.where(shapes_tbl.c.created_by_user_id == user_id)
    if organization_id is not None:
        stmt = stmt.where(shapes_tbl.c.organization_id == organization_id)
    if namespace_id is not None:
        stmt = stmt.where(shapes_tbl.c.namespace_id == namespace_id)
    res = conn.execute(stmt)
    for row in res:
        yield GeoShapeMetadata.parse_obj(dict(row))


def get_shape_metadata_by_bounding_box(
    conn: Connection,
    bbox: ViewportBounds,
    limit: int = None,
    offset: int = 0,
) -> List[GeoShapeMetadata]:
    """Get all shapes within a bounding box.

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
        select(shapes_tbl)  # type: ignore
        .with_only_columns(METADATA_COLS)
        .where(shapes_tbl.c.deleted_at == None)
        .where(
            # Check if the shape intersects with the bounding box
            func.ST_Intersects(
                shapes_tbl.c.geom,
                func.ST_GeomFromText(
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
    return [GeoShapeMetadata.parse_obj(dict(g)) for g in list(res)]


def get_shape_metadata_matching_search(
    conn: Connection, search_query: str, limit: Optional[int] = None, offset: int = 0
) -> List[GeoShapeMetadata]:
    """Get all shapes matching a search string."""
    stmt = sa.text(
        """
        SELECT uuid
        , name
        , properties - '__uuid' AS properties
        , created_at
        , updated_at
        , ts_rank_cd(fts, query, 12) AS rank
        , namespace_id
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
    return [GeoShapeMetadata.parse_obj(dict(g)) for g in list(res)]


def get_all_shape_metadata_by_organization(
    conn: Connection,
    organization_id: UUID4,
    limit: Optional[int] = None,
    offset: int = 0,
) -> List[GeoShapeMetadata]:
    # TODO remove UUID ordering
    return list(
        select_shape_metadata(
            conn, organization_id=organization_id, limit=limit, offset=offset
        )
    )


## Updating ###


def update_shape(
    conn: Connection,
    id_: UUID4,
    *,
    user_id: int,
    namespace_id: Optional[UUID4] = None,
    geojson: Optional[Feature] = None,
) -> GeoShape:
    """Update a shape with additional information."""
    values: Dict[str, Any] = {"updated_by_user_id": user_id}
    if namespace_id:
        values["namespace_id"] = namespace_id
    if geojson:
        values["geojson"] = geojson.dict()
    stmt = (
        update(shapes_tbl)
        .where(shapes_tbl.c.uuid == id_)
        .returning(
            shapes_tbl.c.uuid,
            shapes_tbl.c.created_at,
            shapes_tbl.c.updated_at,
            shapes_tbl.c.geojson,
            shapes_tbl.c.namespace_id,
        )
    )
    res = conn.execute(stmt, values).first()
    if res is None:
        raise ShapeDoesNotExist(id_)
    # The trigger that updates properties from geojson does not run until
    # after returning retrieves values for the row. the following lines
    # work around that
    new_shape = dict(res)
    new_shape["properties"] = new_shape["geojson"]["properties"]
    new_shape["name"] = new_shape["properties"]["name"]
    return GeoShape.parse_obj(new_shape)


### Deleting ###


def delete_shape(conn: Connection, id_: UUID4, *, user_id: int) -> None:
    """Delete a shape."""
    values = {
        "deleted_at": datetime.datetime.now(),
        "deleted_by_user_id": user_id,
    }
    stmt = update(shapes_tbl).where(shapes_tbl.c.uuid == id_)
    res = conn.execute(stmt, values)
    if not res.rowcount:
        raise ShapeDoesNotExist(id_)
    return None


def delete_many_shapes(
    conn: Connection,
    *,
    user_id: int,
    ids: Optional[Sequence[UUID4]] = None,
    namespace_id: Optional[UUID4] = None,
    organization_id: Optional[UUID4] = None,
) -> List[UUID4]:
    """Delete many shapes."""
    values = {
        "deleted_at": datetime.datetime.now(),
        "deleted_by_user_id": user_id,
    }
    stmt = (
        update(shapes_tbl)
        .where(shapes_tbl.c.deleted_at.is_(None))
        .returning(shapes_tbl.c.uuid)
    )
    if namespace_id:
        stmt = stmt.where(shapes_tbl.c.namespace_id == namespace_id)
    if organization_id:
        stmt = stmt.where(shapes_tbl.c.organization_id == organization_id)
    if user_id:
        stmt = stmt.where(shapes_tbl.c.created_by_user_id == user_id)
    # TODO: should this raise an exception if ids are expplicitly
    if ids:
        stmt = stmt.where(shapes_tbl.c.uuid.in_(ids))
    res = conn.execute(stmt, values)
    return [row.uuid for row in res.fetchall()]


def get_shape_count(conn: Connection) -> int:
    """Get the number of shapes in an organization."""
    stmt = (
        sa.select(sa.func.count(shapes_tbl.c.uuid))
        .where(shapes_tbl.c.organization_id == sa.func.app_user_org())
        .where(shapes_tbl.c.deleted_at == None)
    )
    return conn.execute(stmt).scalar()


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
        return [GeoShape.parse_obj(dict(row)).geojson for row in res]
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
        return [GeoShape.parse_obj(dict(row)).geojson for row in res]
    return []
