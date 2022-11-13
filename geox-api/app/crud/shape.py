"""CRUD functions for interacting with shapes.

NOTE: All queries use `shapes` table and no ORM features
"""
import datetime
import logging
from enum import Enum
from typing import (
    Any,
    Dict,
    Generator,
    List,
    Optional,
    Sequence,
    Set,
    TypeVar,
    Union,
    cast,
)

import jinja2
import sqlalchemy as sa
from geojson_pydantic import Feature, GeometryCollection, LineString, Point, Polygon
from geojson_pydantic.geometries import Geometry
from pydantic import UUID4  # pylint: disable=no-name-in-module
from sqlalchemy import String, and_, func, insert, or_, select, update
from sqlalchemy.engine import Connection
from sqlalchemy.sql import ColumnElement, Select, bindparam

from app.core.datatypes import MapProjection
from app.crud.namespaces import get_default_namespace
from app.db.metadata import shapes as shapes_tbl
from app.schemas import GeoShape, GeoShapeCreate, GeoShapeMetadata, ViewportBounds

T = TypeVar("T")

logger = logging.getLogger(__name__)


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

# Read Shapes


class ShapeDoesNotExist(Exception):
    def __init__(self, id_: UUID4) -> None:
        self.id = id_

    def __str__(self) -> str:
        return f"Shape {self.id} does not exist."


# Create Shapes


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
            namespace_id=namespace_id or get_default_namespace(conn, organization_id).id,
            geom=func.ST_GeomFromGeoJSON(bindparam("geom")),
        )
        .returning(*GEOSHAPE_COLS)
    )  # type: ignore
    values = {
        **_parse_shape_args(geojson=geojson, name=name, properties=properties, geom=geom),
    }
    values["properties"] = values.get("properties") or {}
    res = conn.execute(stmt, values).first()
    return GeoShape.from_orm(res)


def _get_name(d: Dict[str, Any]) -> Optional[str]:
    for k in d:
        if str(k).lower().strip() == "name" and d[k]:
            return str(d[k])
    return None


def _parse_shape_args(
    *,
    geojson: Optional[Feature] = None,
    geom: Union[None, Geometry, GeometryCollection] = None,
    properties: Optional[Dict[str, Any]] = None,
    name: Optional[str] = None,
    keep_none: bool = False,
) -> Dict[str, Any]:
    """Combine geojson objects with components."""
    out: Dict[str, Any] = {"name": None, "properties": None, "geom": None}
    # Geom
    geom_new = None
    if geom:
        geom_new = geom
    if geojson is not None:
        geom_new = geojson.geometry
    if geom_new is not None:
        # returning geom as a string makes it easier to include as a param in input/update queries
        out["geom"] = geom_new.json()

    # Name
    name_new = None
    # Ignore some values that are not names
    if name and name.lower() not in {"New shape", "New upload"}:
        name_new = name
    elif name_new := _get_name(properties or {}):
        pass
    elif name_new := _get_name(geojson.properties or {}) if geojson else None:
        pass
    elif name:
        name_new = name
    if name_new:
        out["name"] = str(name_new)

    # This allows {} to remove properties
    # Properties
    properties_new: Optional[Dict[str, Any]] = None
    if properties is not None:
        properties_new = properties
    elif geojson is not None and geojson.properties is not None:
        properties_new = {**geojson.properties}
    if properties_new is not None:
        delete_keys: Set[str] = {"__uuid"}
        properties_new = {
            k: v
            for k, v in properties_new.items()
            if k not in delete_keys and str(k).lower().strip() != "name"
        }
        out["properties"] = properties_new
    if keep_none:
        return out
    return {k: v for k, v in out.items() if v is not None}


def create_many_shapes(
    conn: Connection,
    data: Sequence[GeoShapeCreate],
    user_id: int,
    organization_id: UUID4,
    namespace_id: Optional[UUID4] = None,
) -> Generator[Union[UUID4, GeoShape], None, None]:
    """Create many new shapes."""
    stmt = (
        insert(shapes_tbl)  # type: ignore
        .values(
            created_by_user_id=user_id,
            updated_by_user_id=user_id,
            organization_id=organization_id,
            geom=func.ST_GeomFromGeoJSON(func.cast(bindparam("geom"), String)),
        )
        .returning(*GEOSHAPE_COLS)
    )
    default_namespace = namespace_id or get_default_namespace(conn, organization_id).id
    params = [
        {
            **_parse_shape_args(
                geojson=x.geojson,
                name=x.name,
                properties=x.properties,
                geom=x.geometry,
                keep_none=True,
            ),
            "namespace_id": x.namespace or default_namespace,
        }
        for x in data
    ]
    new_shapes = conn.execute(stmt, params)
    for row in new_shapes:
        yield GeoShape.parse_obj(dict(row))


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
    shape_id: Union[None, UUID4, Sequence[UUID4]] = None,
    created_by_user_id: Union[None, int, Sequence[int]] = None,
    organization_id: Union[None, UUID4, Sequence[UUID4]] = None,
    namespace_id: Union[None, UUID4, Sequence[UUID4]] = None,
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
    if shape_id:
        stmt = stmt.where(shapes_tbl.c.uuid.in_(listify(shape_id)))
    if created_by_user_id is not None:
        stmt = stmt.where(
            shapes_tbl.c.created_by_user_id.in_(listify(created_by_user_id))
        )
    if namespace_id:
        stmt = stmt.where(shapes_tbl.c.namespace_id.in_(listify(namespace_id)))
    if organization_id:
        stmt = stmt.where(shapes_tbl.c.organization_id.in_(listify(organization_id)))
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
    # Awlays order by ID
    stmt = stmt.order_by(shapes_tbl.c.uuid)

    return stmt


def select_shapes(
    conn: Connection,
    *,
    shape_id: Union[None, UUID4, Sequence[UUID4]] = None,
    created_by_user_id: Union[None, int, Sequence[int]] = None,
    organization_id: Union[None, UUID4, Sequence[UUID4]] = None,
    namespace_id: Union[None, UUID4, Sequence[UUID4]] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = 0,
    bbox: Optional[ViewportBounds] = None,
) -> Generator[GeoShape, None, None]:
    # This will be called many times - use more advanced caching
    stmt = _select_shapes_query(
        created_by_user_id=created_by_user_id,
        organization_id=organization_id,
        namespace_id=namespace_id,
        limit=limit,
        offset=offset,
        bbox=bbox,
        shape_id=shape_id,
        columns=GEOSHAPE_COLS,
    )
    res = conn.execute(stmt)
    for row in res:
        yield GeoShape.parse_obj(dict(row))


def select_shape_metadata(
    conn: Connection,
    *,
    shape_id: Union[None, UUID4, Sequence[UUID4]] = None,
    created_by_user_id: Union[None, int, Sequence[int]] = None,
    organization_id: Union[None, UUID4, Sequence[UUID4]] = None,
    namespace_id: Union[None, UUID4, Sequence[UUID4]] = None,
    bbox: Optional[ViewportBounds] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = 0,
) -> Generator[GeoShapeMetadata, None, None]:
    """Query shape metadata."""
    # This will be called many times - use more advanced caching
    stmt = _select_shapes_query(
        created_by_user_id=created_by_user_id,
        organization_id=organization_id,
        namespace_id=namespace_id,
        limit=limit,
        offset=offset,
        bbox=bbox,
        shape_id=shape_id,
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


def listify(value: T) -> List[T]:
    """Optionally convert single value into a list."""
    if isinstance(value, (str, bytes)):
        return [cast(T, value)]
    if isinstance(value, Sequence):
        return list(value)
    return [value]


def delete_many_shapes(
    conn: Connection,
    *,
    user_id: int,
    shape_id: Union[None, Sequence[UUID4], UUID4] = None,
    namespace_id: Union[None, Sequence[UUID4], UUID4] = None,
    organization_id: Union[None, Sequence[UUID4], UUID4] = None,
    created_by_user_id: Union[None, Sequence[int], UUID4] = None,
    exclusive: bool = False,
) -> List[UUID4]:
    """Delete many shapes.

    Args:
        user_id: The id of the user deleting the shapes.
        created_by_user_id: Delete shapes by this user.
        exclusive: If `True`, then conditions are combined with `AND`;
            If `False`, then conditions are combined with `OR`.  The
            default is `False` so that if no conditions are specified,
            no shapes are deleted.  To delete all shapes in an organization with
            an `app_user` either set `exclusive=True` with no other args,
            or set `exclusive=False` with an `organization_id`.
    Returns:
        List of shape IDs that were deleted.

    """
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
        filters.append(shapes_tbl.c.namespace_id.in_(listify(namespace_id)))
    if organization_id:
        filters.append(shapes_tbl.c.organization_id.in_(listify(organization_id)))
    if created_by_user_id:
        filters.append(shapes_tbl.c.created_by_user_id.in_(listify(created_by_user_id)))
    if shape_id:
        filters.append(shapes_tbl.c.uuid.in_(listify(shape_id)))
    if exclusive:
        stmt = stmt.where(and_(True, *filters))
    else:
        stmt = stmt.where(or_(False, *filters))
    res = conn.execute(stmt, values)
    return [row.uuid for row in res]


def get_shape_count(conn: Connection) -> int:
    """Get the number of shapes in an organization."""
    stmt = (
        sa.select(sa.func.count(shapes_tbl.c.uuid))
        .where(shapes_tbl.c.organization_id == sa.func.app_user_org())
        .where(shapes_tbl.c.deleted_at.is_(None))
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
