"""CRUD functions for interacting with shapes."""
import datetime
from typing import List, Optional, Sequence
from uuid import UUID

from sqlalchemy import func, insert, select, update
from sqlalchemy.orm import Session

from app import schemas
from app.models import Shape


def get_shape(db: Session, shape: schemas.GeoShapeRead) -> Optional[schemas.GeoShape]:
    """Get a shape."""
    query = (
        select(Shape)  # type: ignore
        .filter(Shape.deleted_at == None)
        .filter(Shape.uuid == shape.uuid)
        .limit(1)
    )
    res = db.execute(query).fetchone()
    if res:
        return schemas.GeoShape.from_orm(res[0])
    return None


def get_all_shapes_by_user(db: Session, user_id: int) -> List[schemas.GeoShape]:
    """Get all shapes created by a user."""
    stmt = (
        select(Shape)
        .where(  # type: ignore
            Shape.created_by_user_id == user_id, Shape.deleted_at == None
        )
        .order_by(Shape.updated_at.desc())
    )
    res = db.execute(stmt).scalars().fetchall()
    return [schemas.GeoShape.from_orm(g) for g in list(res)]


def get_all_shapes_by_organization(
    db: Session, organization_id: UUID
) -> List[schemas.GeoShape]:
    """Get all shapes for an organization."""
    # This is usually equivalent to getting all shapes by organization
    stmt = (
        select(Shape)
        .where(  # type: ignore
            Shape.organization_id == str(organization_id), Shape.deleted_at == None
        )
        .order_by(Shape.updated_at.desc())
    )
    res = db.execute(stmt).scalars().fetchall()
    return [schemas.GeoShape.from_orm(g) for g in list(res)]


def get_all_shapes(db: Session) -> List[schemas.GeoShape]:
    """Get all shapes which the user has permission."""
    # This will effectively get all shapes for the organization given RLS
    stmt = select(Shape).where(Shape.deleted_at == None)  # type: ignore
    res = db.execute(stmt)
    return [schemas.GeoShape.parse_obj(g) for g in res]


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
            geojson=geoshape.geojson.json(),
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
        ins, [{"name": s.name, "geojson": s.geojson.json()} for s in geoshapes]
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
        values["geojson"] = geoshape.geojson.json()
    stmt = (
        update(Shape)  # type: ignore
        .values(**values)
        .where(Shape.uuid == str(geoshape.uuid))
        .returning(Shape)  # type: ignore
    )
    res = db.execute(stmt)
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


def delete_many_shapes(db: Session, uuids: Sequence[str]) -> int:
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
