"""CRUD functions for interacting with shapes.

NOTE: All queries use Shape table and no ORM features
"""
import datetime
from enum import Enum
from typing import List, Optional, Sequence, Union

import jinja2
import sqlalchemy as sa
from geojson_pydantic import Feature, LineString, Point, Polygon
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import schemas
from app.models import Shape


shape_tbl = Shape.__table__


DEFAULT_LIMIT = 200
METADATA_COLS = [
    shape_tbl.c.uuid,
    shape_tbl.c.name,
    shape_tbl.c.properties,
    shape_tbl.c.created_at,
    shape_tbl.c.updated_at,
]


def get_shape(db: Session, shape_id: UUID4) -> Optional[schemas.GeoShape]:
    """Get a shape."""
    query = (
        sa.select(shape_tbl)
        .where(shape_tbl.c.deleted_at == None)
        .where(shape_tbl.c.uuid == shape_id)
        .limit(1)
    )
    res = db.execute(query).first()
    if res:
        return schemas.GeoShape.from_orm(res)
    return None


def get_all_shapes_by_user(
    db: Session, user_id: int, offset: int = 0, limit: Optional[int] = DEFAULT_LIMIT
) -> List[schemas.GeoShape]:
    """Get all shapes created by a user."""
    # TODO ordering by UUID just guarantees a sort order
    # I am only doing this because the selected feature index in nebula.gl
    # on the frontend needs consistent
    # We should find a better way of handling this
    stmt = (
        sa.select(shape_tbl)
        .where(shape_tbl.c.created_by_user_id == user_id)
        .where(shape_tbl.c.deleted_at == None)
        .order_by(shape_tbl.c.uuid)
        .offset(offset)
    )
    if limit is not None:
        stmt = stmt.limit(limit)
    res = db.execute(stmt).fetchall()
    return [schemas.GeoShape.from_orm(g) for g in list(res)]


def get_shape_metadata_by_bounding_box(db: Session, bbox: schemas.ViewportBounds, offset: int = 0, limit: int = DEFAULT_LIMIT) -> List[schemas.GeoShapeMetadata]:
    """Get all shapes within a bounding box

    Used on the frontend to determine which shapes to show details on in the sidebar
    """
    geom = Polygon(type="Polygon", coordinates=[[
        (bbox.minX, bbox.minY),
        (bbox.minX, bbox.maxY),
        (bbox.maxX, bbox.maxY),
        (bbox.maxX, bbox.minY),
        (bbox.minX, bbox.minY)
    ]])
    stmt = (
        sa.select(shape_tbl)
        .with_only_columns(METADATA_COLS)
        .where(
            shape_tbl.c.deleted_at == None
        )
        .where(
            sa.func.ST_Intersects(
                shape_tbl.c.geom, sa.func.ST_Transform(geom, 4326))
        )
        .order_by(shape_tbl.c.uuid)
        .offset(offset)
        .limit(limit)
    )
    res = db.execute(stmt).fetchall()
    return [schemas.GeoShapeMetadata.from_orm(g) for g in list(res)]


def get_shape_metadata_matching_search(db: Session, query: str, offset: int = 0, limit: int = DEFAULT_LIMIT) -> List[schemas.GeoShapeMetadata]:
    """Get all shapes matching a search string."""
    stmt = sa.text("""
        SELECT uuid
        , name
        , properties
        , created_at
        , updated_at
        , ts_rank_cd(fts, query, 12) AS rank
        FROM shapes
        , websearch_to_tsquery(:query_text) query
        , SIMILARITY(:query_text, properties::VARCHAR) similarity
        WHERE 1=1
          AND (query @@ fts OR similarity > 0)
        ORDER BY rank DESC, similarity DESC
        LIMIT 20
        OFFSET :offset
    """)
    res = db.execute(stmt, {
        "query_text": query,
        "offset": offset
    }).scalars().fetchall()
    return [schemas.GeoShapeMetadata.from_orm(g) for g in list(res)]


def get_all_shapes_by_organization(
    db: Session, organization_id: UUID4, offset: int = 0, limit: Optional[int] = DEFAULT_LIMIT
) -> List[schemas.GeoShape]:
    # This is usually equivalent to getting all shapes by organization
    # TODO ordering by UUID just guarantees a sort order
    # I am only doing this because the selected feature index in nebula.gl
    # on the frontend needs consistent
    # We should find a better way of handling this
    stmt = (
        sa.select(shape_tbl)
        .where(shape_tbl.c.organization_id == str(organization_id))  # type: ignore
        .where(shape_tbl.c.deleted_at == None)
        .order_by(shape_tbl.c.uuid)
        .offset(offset)
        .limit(limit)
    )
    res = db.execute(stmt).fetchall()
    return [schemas.GeoShape.from_orm(g) for g in list(res)]


def get_all_shape_metadata_by_organization(
    db: Session, organization_id: UUID4, offset: int = 0, limit: Optional[int] = DEFAULT_LIMIT
) -> List[schemas.GeoShapeMetadata]:
    stmt = (
        sa.select(shape_tbl)
        .with_only_columns(METADATA_COLS)
        .where(shape_tbl.c.organization_id == str(organization_id))  # type: ignore
        .where(shape_tbl.c.deleted_at == None)
        .order_by(shape_tbl.c.uuid)
        .offset(offset)
        .limit(limit)
    )
    res = db.execute(stmt).fetchall()
    return [schemas.GeoShapeMetadata.from_orm(g) for g in list(res)]


def create_shape(db: Session, geoshape: schemas.GeoShapeCreate) -> schemas.GeoShape:
    """Create a new shape"""
    ins = (
        sa.insert(shape_tbl)  # type: ignore
        .values(
            created_by_user_id=sa.func.app_user_id(),
            updated_by_user_id=sa.func.app_user_id(),
            updated_at=sa.func.now(),
            created_at=sa.func.now(),
            organization_id=sa.func.app_user_org(),
            name=geoshape.name,
            geojson=geoshape.geojson.dict(),
        )
        .returning(shape_tbl)  # type: ignore
    )
    new_shape = db.execute(ins).fetchone()
    res = schemas.GeoShape.from_orm(new_shape)
    return res


def create_many_shapes(
    db: Session, geoshapes: Sequence[schemas.GeoShapeCreate]
) -> List[UUID4]:
    """Create many new shapes."""
    ins = (
        sa.insert(shape_tbl)  # type: ignore
        .values(
            created_by_user_id=sa.func.app_user_id(),
            created_at=sa.func.now(),
            updated_by_user_id=sa.func.app_user_id(),
            updated_at=sa.func.now(),
            organization_id=sa.func.app_user_org(),
        )
        .returning(shape_tbl.c.uuid)
    )
    new_shapes = db.execute(
        ins, [{"name": s.name, "geojson": s.geojson.dict()} for s in geoshapes]
    ).scalars()
    return list(new_shapes)


def update_shape(db: Session, geoshape: schemas.GeoShapeUpdate) -> schemas.GeoShape:
    """Update a shape with additional information."""
    values = {
        "name": geoshape.name,
        "updated_at": datetime.datetime.now(),
        "updated_by_user_id": sa.func.app_user_id(),
    }
    if geoshape.geojson:
        values["geojson"] = geoshape.geojson.dict()
    update_stmt = (
        sa.update(shape_tbl)
        .values(**values)
        .where(shape_tbl.c.uuid == str(geoshape.uuid))
        .returning(shape_tbl)
    )
    res = db.execute(update_stmt)
    rows = res.rowcount
    if rows == 0:
        raise Exception("No rows updated")
    shape = res.fetchone()
    return schemas.GeoShape.from_orm(shape)


def delete_shape(db: Session, uuid: UUID4) -> int:
    """Delete a shape."""
    # TODO: What to do if exists?
    values = {
        "deleted_at": datetime.datetime.now(),
        "deleted_by_user_id": sa.func.app_user_id(),
    }
    stmt = (
        sa.update(shape_tbl)
        .values(**values)
        .where(shape_tbl.c.uuid == str(uuid))
        .returning(shape_tbl.c.uuid)  # type: ignore
    )
    res = db.execute(stmt)
    rows = res.rowcount
    return rows


def delete_many_shapes(db: Session, uuids: Sequence[UUID4]) -> int:
    """Delete a shape."""
    # TODO: What to do if exists?
    values = {
        "deleted_at": datetime.datetime.now(),
        "deleted_by_user_id": sa.func.app_user_id(),
    }
    stmt = (
        sa.update(shape_tbl)
        .values(**values)
        .where(shape_tbl.c.uuid.in_(tuple([str(x) for x in uuids])))
    )  # type: ignore
    res = db.execute(stmt)
    rows = res.rowcount
    return rows


def get_shape_count(db: Session) -> int:
    """Get the number of shapes in an organization."""
    stmt = (
        sa.select(sa.func.count(shape_tbl.c.uuid))
        .where(shape_tbl.c.organization_id == sa.func.app_user_org())
        .where(shape_tbl.c.deleted_at == None)
    )
    res = db.execute(stmt).fetchone()
    return res[0]


def get_shapes_containing_point(db: Session, lat: float, lng: float) -> List[Feature]:
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
    res = db.execute(stmt, {"lat": lat, "lng": lng}).fetchall()
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
    db: Session, operation: GeometryOperation, geom: Union[Point, Polygon, LineString]
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
    res = db.execute(stmt, {"geom": geom.json()}).fetchall()
    if res:
        return [schemas.GeoShape.from_orm(row).geojson for row in res]
    return []
