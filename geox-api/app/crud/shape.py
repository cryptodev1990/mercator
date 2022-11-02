"""CRUD functions for interacting with shapes.

NOTE: All queries use `shapes` table and no ORM features
"""
import datetime
import logging
from enum import Enum
from typing import Any, Dict, Generator, List, Optional, Sequence, Union

import jinja2
import sqlalchemy as sa
from geojson_pydantic import Feature, GeometryCollection, LineString, Point, Polygon
from geojson_pydantic.geometries import Geometry
from pydantic import UUID4
from sqlalchemy import String, and_, func, insert, or_, select, update
from sqlalchemy.engine import Connection
from sqlalchemy.sql import ColumnElement, Select, bindparam

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
    func.shape_geojson(
        shapes_tbl.c.uuid, shapes_tbl.c.geom, shapes_tbl.c.properties, shapes_tbl.c.name
    ).label("geojson"),
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
    organization_id: UUID4,
    name: Optional[str] = None,
    namespace_id: Optional[UUID4] = None,
    geom: Union[None, Geometry, GeometryCollection] = None,
    properties: Optional[Dict[str, Any]] = None,
    geojson: Optional[Feature] = None,
) -> GeoShape:
    """Create a new shape."""
    # The trigger that updates properties from geojson does not run until
    # after returning retrieves values for the row. the following lines
    # work around that
    stmt = (
        insert(shapes_tbl)
        .values(
            created_by_user_id=user_id,
            updated_by_user_id=user_id,
            organization_id=organization_id,
            namespace_id=namespace_id
            or get_default_namespace(conn, organization_id).id,
            geom=func.ST_GeomFromGeoJSON(bindparam("geom")),
        )
        .returning(*GEOSHAPE_COLS)
    )  # type: ignore
    values = {
        **_parse_shape_args(
            geojson=geojson, name=name, properties=properties, geom=geom
        ),
    }
    values["properties"] = values.get("properties") or {}
    res = conn.execute(stmt, values).first()
    return GeoShape.from_orm(res)


def _parse_shape_args(
    *,
    geojson: Optional[Feature],
    geom: Union[None, Geometry, GeometryCollection] = None,
    properties: Optional[Dict[str, Any]] = None,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Combine geojson objects with components."""
    out = {}
    # Geom
    geom_new = geom or (geojson.geometry if geojson is not None else geojson)
    if geom_new is not None:
        # returning geom as a string makes it easier to include as a param in input/update queries
        out["geom"] = geom_new.json()
    properties_new = (properties if properties is not None else None) or (
        geojson.properties if geojson is not None else None
    )
    # Properties
    if properties_new is not None:
        out["properties"] = properties_new
        for k in ("__uuid", "name"):
            try:
                del properties_new[k]
            except KeyError:
                pass
    # Name
    name_new = (
        name
        or (properties or {}).get("name")
        or ((geojson.properties or {}).get("name") if geojson is not None else None)
    )
    if name_new is not None:
        out["name"] = name_new
    return out


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
            geom=func.ST_GeomFromGeoJSON(func.cast(bindparam("geom"), String)),
        )
        .returning(shapes_tbl.c.uuid)
    )
    ## TODO: remove exception after migration
    default_namespace = namespace_id or get_default_namespace(conn, organization_id).id
    params = [
        {
            **_parse_shape_args(
                geojson=x.geojson, name=x.name, properties=x.properties, geom=x.geometry
            ),
            "namespace_id": x.namespace or default_namespace,
        }
        for x in data
    ]
    new_shapes = conn.execute(stmt, params)
    for row in new_shapes:
        yield row.uuid


def shape_exists(conn: Connection, shape_id: UUID4, include_deleted=False) -> bool:
    stmt = select(shapes_tbl.c.uuid).where(shapes_tbl.c.uuid == shape_id)  # type: ignore
    if not include_deleted:
        stmt = stmt.where(shapes_tbl.c.deleted_at.is_(None))
    return bool(conn.execute(stmt).scalar())


def get_shape(conn: Connection, shape_id: UUID4, include_deleted=False) -> GeoShape:
    """Get a shape."""
    stmt = select(GEOSHAPE_COLS).where(shapes_tbl.c.uuid == shape_id)  # type: ignore
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
        **_parse_shape_args(
            geojson=geojson,
            geom=geometry,
            name=name,
            properties=properties,
        ),
    }
    params = {}
    if values.get("geom"):
        # Need to transform
        params["geom"] = values["geom"]
        values["geom"] = func.ST_GeomFromGeoJSON(func.cast(bindparam("geom"), String))
    # If geojson is not specified, then these are updated.
    if namespace_id:
        values["namespace_id"] = namespace_id
    stmt = (
        update(shapes_tbl)
        .where(shapes_tbl.c.uuid == id_)
        .values(**values)
        .returning(*GEOSHAPE_COLS)
    )
    res = conn.execute(stmt, params).first()
    print(res)
    if res is None:
        raise ShapeDoesNotExist(id_)
    return GeoShape.from_orm(res)


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
    exclusive: bool = False,
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
    filters = []
    if namespace_id:
        filters.append(shapes_tbl.c.namespace_id == namespace_id)
    if organization_id:
        filters.append(shapes_tbl.c.organization_id == organization_id)
    if user_id:
        filters.append(shapes_tbl.c.created_by_user_id == user_id)
    if ids:
        stmt = stmt.where(shapes_tbl.c.uuid.in_(ids))
    if exclusive:
        stmt = stmt.where(and_(True, *filters))
    else:
        stmt = stmt.where(or_(*filters))
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
    SELECT shape_geojson(uuid, geom, properties, name) AS geojson
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
    SELECT shape_geojson(uuid, geom, properties, name) AS geojson
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
