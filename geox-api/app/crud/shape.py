"""CRUD functions for interacting with shapes.

NOTE: All queries use `shapes` table and no ORM features
"""
import datetime
import logging
from enum import Enum
from typing import Any, Dict, Generator, List, Optional, Sequence, Union
from sqlalchemy.sql import FromClause, ColumnElement
import jinja2
import sqlalchemy as sa
from geojson_pydantic import Feature, GeometryCollection, LineString, Point, Polygon
from geojson_pydantic.geometries import Geometry
from pydantic import UUID4
from sqlalchemy import func, insert, select, update  # type: ignore
from sqlalchemy.engine import Connection
from sqlalchemy.sql import Select
from app.crud.namespaces import get_default_namespace
from app.db.metadata import shapes as shapes_tbl
from app.schemas import GeoShape, GeoShapeCreate, GeoShapeMetadata, ViewportBounds

logger = logging.getLogger(__name__)


class MapProjection(int, Enum):
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

GEOSHAPE_COLS = [
    shapes_tbl.c.uuid,
    shapes_tbl.c.name,
    shapes_tbl.c.namespace_id,
    shapes_tbl.c.created_at,
    shapes_tbl.c.updated_at,
    shapes_tbl.c.geojson,
]

## Read Shapes


class ShapeDoesNotExist(Exception):
    def __init__(self, id_: UUID4) -> None:
        self.id = id_

    def __str__(self) -> str:
        return f"Shape {self.id} does not exist."


## Create Shapes

_select_shapes: Select = select(shapes_tbl).where(shapes_tbl.c.deleted_at.is_(None))  # type: ignore


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
    # The trigger that updates properties from geojson does not run until
    # after returning retrieves values for the row. the following lines
    # work around that
    stmt = insert(shapes_tbl).returning(*GEOSHAPE_COLS)
    values = {
        "created_by_user_id": user_id,
        "updated_by_user_id": user_id,
        "organization_id": organization_id,
        "geojson": _update_geojson(geojson, name=name).dict(),
        "namespace_id": namespace_id or get_default_namespace(conn, organization_id).id,
    }
    res = conn.execute(stmt, values).first()
    return GeoShape.from_orm(res)


def _update_geojson(
    geojson: Feature,
    *,
    geojson_new: Optional[Feature] = None,
    geometry: Union[None, Geometry, GeometryCollection] = None,
    properties: Optional[Dict[str, Any]] = None,
    name: Optional[str] = None,
) -> Feature[Union[Geometry, GeometryCollection], Dict[str, Any]]:
    """Combine geojson objects with components."""
    geometry_new = (
        geometry or (geojson_new.geometry if geojson_new else None) or geojson.geometry
    )
    # where to get the properties from
    properties_new = (
        (
            properties if properties is not None else None
        )  # {} will delete all properties
        or (
            (
                (geojson_new.properties if geojson_new.properties is not None else None)
                if geojson_new
                else None
            )
        )
        or geojson.properties
        or {}
    )
    # where to get the name from
    name_new = (
        name
        or (properties or {}).get("name")
        or (((geojson_new.properties or {}).get("name") if geojson_new else None))
        or (geojson.properties or {}).get("name")
    )
    properties_new["name"] = name_new
    # Remove __uuid and __parent_uuid from properties if they were included
    # This prevents reuploaded data from including a different UUID that may be
    # used by the frontend.
    for k in ("__uuid", "__parent_uuid"):
        try:
            del properties_new[k]
        except KeyError:
            pass
    return Feature.parse_obj({"geometry": geometry_new, "properties": properties_new})


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
            "geojson": _update_geojson(x.geojson, name=x.name).dict(),
            "namespace_id": x.namespace or default_namespace,
        }
        for x in data
    ]
    new_shapes = conn.execute(stmt, values)
    for row in new_shapes:
        yield row.uuid


def shape_exists(conn: Connection, shape_id: UUID4, include_deleted=False) -> bool:
    stmt = select(shapes_tbl.c.uuid).where(shapes_tbl.c.uuid == shape_id)  # type: ignore
    if not include_deleted:
        stmt = stmt.where(shapes_tbl.c.deleted_at.is_(None))
    return bool(conn.execute(stmt).scalar())


def get_shape(conn: Connection, shape_id: UUID4, include_deleted=False) -> GeoShape:
    """Get a shape."""
    stmt = select(shapes_tbl).where(shapes_tbl.c.uuid == shape_id)  # type: ignore
    if not include_deleted:
        stmt = stmt.where(shapes_tbl.c.deleted_at.is_(None))
    res = conn.execute(stmt).first()
    if res is None:
        raise ShapeDoesNotExist(shape_id)
    return GeoShape.parse_obj(dict(res))


def _select_shapes_query(
    ids: Optional[Sequence[UUID4]] = None,
    user_id: Optional[int] = None,
    organization_id: Optional[UUID4] = None,
    namespace_id: Optional[UUID4] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = 0,
    bbox: Optional[ViewportBounds] = None,
    columns: Optional[Sequence[Union[ColumnElement[Any], int, str]]] = None,
) -> Select:
    if columns:
        cols = [shapes_tbl.c[c] if isinstance(c, str) else c for c in columns]
        stmt = select(cols)
    else:
        stmt = select(shapes_tbl)  # type: ignore
    stmt = stmt.where(shapes_tbl.c.deleted_at.is_(None))
    if ids is not None:
        stmt = stmt.where(shapes_tbl.c.uuid.in_(ids))
    if user_id is not None:
        stmt = stmt.where(shapes_tbl.c.created_by_user_id == user_id)
    if namespace_id is not None:
        stmt = stmt.where(shapes_tbl.c.namespace_id == namespace_id)
    if organization_id is not None:
        stmt = stmt.where(shapes_tbl.c.organization_id == organization_id)
    if bbox:
        stmt = stmt.where(
            func.ST_Intersects(
                shapes_tbl.c.geom,
                func.ST_MakeEnvelope(
                    bbox.min_x, bbox.min_y, bbox.max_x, bbox.max_y, MapProjection.WGS84
                ),
            )
        )
    if limit:
        stmt = stmt.limit(limit)
    if offset is not None:
        stmt = stmt.offset(offset)

    return stmt


def select_shapes(
    conn: Connection,
    *,
    ids: Optional[Sequence[UUID4]] = None,
    user_id: Optional[int] = None,
    organization_id: Optional[UUID4] = None,
    namespace_id: Optional[UUID4] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = 0,
    bbox: Optional[ViewportBounds] = None,
) -> Generator[GeoShape, None, None]:
    # This will be called many times - use more advanced caching
    stmt = _select_shapes_query(
        user_id=user_id,
        organization_id=organization_id,
        namespace_id=namespace_id,
        limit=limit,
        offset=offset,
        bbox=bbox,
        ids=ids,
        columns=GEOSHAPE_COLS,
    )
    res = conn.execute(stmt)
    for row in res:
        yield GeoShape.parse_obj(dict(row))


def select_shape_metadata(
    conn: Connection,
    *,
    ids: Optional[Sequence[UUID4]] = None,
    bbox: Optional[ViewportBounds] = None,
    user_id: Optional[int] = None,
    organization_id: Optional[UUID4] = None,
    namespace_id: Optional[UUID4] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = 0,
) -> Generator[GeoShapeMetadata, None, None]:
    """Query shape metadata."""
    # This will be called many times - use more advanced caching
    stmt = _select_shapes_query(
        user_id=user_id,
        organization_id=organization_id,
        namespace_id=namespace_id,
        limit=limit,
        offset=offset,
        bbox=bbox,
        ids=ids,
        columns=METADATA_COLS,
    )
    res = conn.execute(stmt)
    for row in res:
        yield GeoShapeMetadata.parse_obj(dict(row))


def get_shape_metadata_matching_search(
    conn: Connection, search_query: str, limit: Optional[int] = None, offset: int = 0
) -> List[GeoShapeMetadata]:
    """Get all shapes matching a search string."""
    stmt = sa.text(
        """
        SELECT
          uuid
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
          AND deleted_at IS NULL
        ORDER BY rank DESC, similarity DESC
        LIMIT :limit
        OFFSET :offset
    """
    )
    res = conn.execute(
        stmt, {"query_text": search_query, "limit": limit, "offset": offset}
    ).fetchall()
    return [GeoShapeMetadata.parse_obj(dict(g)) for g in list(res)]


## Updating ###


def update_shape(
    conn: Connection,
    id_: UUID4,
    *,
    user_id: int,
    namespace_id: Optional[UUID4] = None,
    geojson: Optional[Feature] = None,  # type: ignore
    geometry: Union[None, Geometry, GeometryCollection] = None,
    properties: Optional[Dict[str, Any]] = None,
    name: Optional[str] = None,
) -> GeoShape:
    """Update a shape with additional information."""
    values: Dict[str, Any] = {
        "updated_by_user_id": user_id,
        "updated_at": datetime.datetime.utcnow(),
    }
    # If geojson is not specified, then these are updated.
    values["geojson"] = _update_geojson(
        get_shape(conn, id_).geojson,
        geojson_new=geojson,
        geometry=geometry,
        name=name,
        properties=properties,
    ).dict()
    if namespace_id:
        values["namespace_id"] = namespace_id
    stmt = update(shapes_tbl).where(shapes_tbl.c.uuid == id_).returning(*GEOSHAPE_COLS)
    res = conn.execute(stmt, values).first()
    if res is None:
        raise ShapeDoesNotExist(id_)
    # The trigger that updates properties from geojson does not run until
    # after returning retrieves values for the row. the following lines
    # work around that
    return GeoShape.parse_obj(res)


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
    return [row.uuid for row in res]


def get_shape_count(conn: Connection) -> int:
    """Get the number of shapes in an organization."""
    stmt = (
        sa.select(sa.func.count(shapes_tbl.c.uuid))
        .where(shapes_tbl.c.organization_id == sa.func.app_user_org())
        .where(shapes_tbl.c.deleted_at == None)
    )
    res = conn.execute(stmt).scalar()
    return res


def get_shapes_containing_point(
    conn: Connection, lat: float, lng: float
) -> List[Feature]:
    """Get the shape that contains a point."""
    stmt = sa.text(
        """
    SELECT geojson
    FROM shapes
    WHERE 1=1
      AND ST_Contains(geom, ST_GeomFromText('POINT(:lng :lat)', 4326))
      AND deleted_at IS NULL
      AND organization_id = public.app_user_org()
    """
    )
    res = conn.execute(stmt, {"lat": lat, "lng": lng}).fetchall()
    return [row.geojson for row in res]


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
    SELECT geojson
    FROM shapes
    WHERE 1=1
      AND ST_{{operation}}(geom, ST_GeomFromGeoJSON(:geom))
      AND deleted_at IS NULL
      AND organization_id = public.app_user_org()
    """
        ).render(operation=operation.title())
    )
    res = conn.execute(stmt, {"geom": geom.json()})
    return [row.geojson for row in res]
