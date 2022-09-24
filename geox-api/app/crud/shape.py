"""CRUD functions for interacting with shapes."""
import datetime
from enum import Enum
from typing import List, Optional, Sequence, Union
from uuid import UUID

import jinja2
from geojson_pydantic import Feature, LineString, Point, Polygon
from sqlalchemy import func, insert, select, text, update
from sqlalchemy.orm import Session

from app import schemas
from app.models import Shape


def get_shape(db: Session, shape: schemas.GeoShapeRead) -> Optional[schemas.GeoShape]:
    """Get a shape."""
    query = (
        select(Shape)
        .where(Shape.deleted_at == None)
        .where(Shape.uuid == shape.uuid)
        .limit(1)
    )
    res = db.execute(query).fetchone()
    if res:
        return schemas.GeoShape.from_orm(res[0])
    return None


def get_all_shapes_by_user(db: Session, user_id: int, offset=0) -> List[schemas.GeoShape]:
    """Get all shapes created by a user."""
    # TODO ordering by UUID just guarantees a sort order
    # I am only doing this because the selected feature index in nebula.gl
    # on the frontend needs consistent
    # We should find a better way of handling this
    stmt = (
        select(Shape)
        .where(
            Shape.created_by_user_id == user_id
        )
        .where(
            Shape.deleted_at == None
        )
        .order_by(Shape.uuid)
    )
    res = db.execute(stmt).scalars().fetchall()
    return [schemas.GeoShape.from_orm(g) for g in list(res)]


def get_all_shapes_by_organization(
    db: Session, organization_id: UUID, offset=0
) -> List[schemas.GeoShape]:
    """Get all shapes for an organization."""
    # This is usually equivalent to getting all shapes by organization
    # TODO ordering by UUID just guarantees a sort order
    # I am only doing this because the selected feature index in nebula.gl
    # on the frontend needs consistent
    # We should find a better way of handling this
    stmt = (
        select(Shape)
        .where(  # type: ignore
            Shape.organization_id == str(
                organization_id)
        )
        .where(
            Shape.deleted_at == None
        )
        .order_by(Shape.uuid)
        .offset(offset)
    )
    res = db.execute(stmt).scalars().fetchall()
    return [schemas.GeoShape.from_orm(g) for g in list(res)]


def create_shape(db: Session, geoshape: schemas.GeoShapeCreate) -> schemas.GeoShape:
    """Create a new shape."""
    ins = (
        insert(Shape)  # type: ignore
        .values(
            created_by_user_id=func.app_user_id(),
            updated_by_user_id=func.app_user_id(),
            updated_at=func.now(),
            created_at=func.now(),
            organization_id=func.app_user_org(),
            name=geoshape.name,
            geojson=geoshape.geojson.dict(),
        )
        .returning(Shape)  # type: ignore
    )
    new_shape = db.execute(ins).fetchone()
    db.commit()
    res = schemas.GeoShape.from_orm(new_shape)
    return res


def create_many_shapes(
    db: Session, geoshapes: Sequence[schemas.GeoShapeCreate]
) -> List[UUID]:
    """Create many new shapes."""
    ins = (
        insert(Shape)  # type: ignore
        .values(
            created_by_user_id=func.app_user_id(),
            created_at=func.now(),
            updated_by_user_id=func.app_user_id(),
            updated_at=func.now(),
            organization_id=func.app_user_org(),
        )
        .returning(Shape.uuid)
    )
    new_shapes = db.execute(
        ins, [{"name": s.name, "geojson": s.geojson.dict()} for s in geoshapes]
    ).scalars()
    db.commit()
    return list(new_shapes)


def update_shape(db: Session, geoshape: schemas.GeoShapeUpdate) -> schemas.GeoShape:
    """Update a shape with additional information."""
    values = {
        "name": geoshape.name,
        "updated_at": datetime.datetime.now(),
        "updated_by_user_id": func.app_user_id(),
    }
    if geoshape.geojson:
        values["geojson"] = geoshape.geojson.dict()
    update_stmt = (
        update(Shape)
        .values(**values)
        .where(Shape.uuid == str(geoshape.uuid))
        .returning(Shape)
    )
    res = db.execute(update_stmt)
    rows = res.rowcount
    db.commit()
    if rows == 0:
        raise Exception("No rows updated")
    shape = res.fetchone()
    return schemas.GeoShape.parse_obj(shape)


def delete_shape(db: Session, uuid: UUID) -> int:
    """Delete a shape."""
    # TODO: What to do if exists?
    values = {
        "deleted_at": datetime.datetime.now(),
        "deleted_by_user_id": func.app_user_id(),
    }
    stmt = (
        update(Shape)
        .values(**values)
        .where(Shape.uuid == str(uuid))
        .returning(Shape.uuid)  # type: ignore
    )
    res = db.execute(stmt)
    rows = res.rowcount
    db.commit()
    return rows


def delete_many_shapes(db: Session, uuids: Sequence[UUID]) -> int:
    """Delete a shape."""
    # TODO: What to do if exists?
    values = {
        "deleted_at": datetime.datetime.now(),
        "deleted_by_user_id": func.app_user_id(),
    }
    stmt = (
        update(Shape)
        .values(**values)
        .where(Shape.uuid.in_(tuple([str(x) for x in uuids])))
    )  # type: ignore
    res = db.execute(stmt)
    rows = res.rowcount
    db.commit()
    return rows


def get_shape_count(db: Session) -> int:
    """Get the number of shapes in an organization."""
    stmt = select(func.count(Shape.uuid)).where(
        Shape.organization_id == func.app_user_org()
    ).where(
        Shape.deleted_at == None
    )
    res = db.execute(stmt).fetchone()
    return res[0]


def get_shapes_containing_point(db: Session, lat: float, lng: float) -> List[Feature]:
    """Get the shape that contains a point."""
    stmt = """
    SELECT *
    FROM shapes
    WHERE 1=1
      AND ST_Contains(geom, ST_GeomFromText('POINT(:lng :lat)', 4326))
      AND deleted_at IS NULL
      AND organization_id = public.app_user_org()
    """
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
    stmt = jinja2.Template(
        """
    SELECT *
    FROM shapes
    WHERE 1=1
      AND ST_{{operation}}(geom, ST_GeomFromGeoJSON(:geom))
      AND deleted_at IS NULL
      AND organization_id = public.app_user_org()
    """
    ).render(operation=operation.title())
    res = db.execute(stmt, {"geom": geom.json()}).fetchall()
    if res:
        return [schemas.GeoShape.from_orm(row).geojson for row in res]
    return []
