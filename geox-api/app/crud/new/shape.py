"""CRUD functions for interacting with shapes."""
import datetime
from typing import List, Optional, Sequence
from uuid import UUID

from sqlalchemy import func, insert, select, update
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session

from app import schemas
from app.models import Shape

shape_tbl = Shape.__table__


def get_shape(
    conn: Connection, shape: schemas.GeoShapeRead
) -> Optional[schemas.GeoShape]:
    """Get a shape."""
    stmt = (
        select(shape_tbl)
        .where(shape_tbl.c.deleted_at == None, shape_tbl.c.uuid == shape.uuid)  # type: ignore
        .limit(1)
    )
    res = conn.execute(stmt).fetchone()
    if res:
        return schemas.GeoShape.from_orm(res)
    return None


def get_all_shapes_by_user(conn: Connection, user_id: int) -> List[schemas.GeoShape]:
    """Get all shapes created by a user."""
    stmt = (
        select(shape_tbl)
        .where(  # type: ignore
            shape_tbl.c.created_by_user_id == user_id, shape_tbl.c.deleted_at == None
        )
        .order_by(shape_tbl.c.updated_at.desc())
    )
    res = conn.execute(stmt).fetchall()
    return [schemas.GeoShape.from_orm(g) for g in list(res)]


def get_all_shapes_by_organization(
    conn: Connection, organization_id: UUID
) -> List[schemas.GeoShape]:
    """Get all shapes for an organization."""
    # This is usually equivalent to getting all shapes by organization
    stmt = (
        select(shape_tbl)
        .where(  # type: ignore
            shape_tbl.c.organization_id == str(organization_id),
            shape_tbl.c.deleted_at.is_(None),
        )
        .order_by(shape_tbl.c.updated_at.desc())
    )
    res = conn.execute(stmt).fetchall()
    return [schemas.GeoShape.from_orm(g) for g in list(res)]


def get_all_shapes(conn: Connection) -> List[schemas.GeoShape]:
    """Get all shapes which the user has permission."""
    # This will effectively get all shapes for the organization given RLS
    stmt = select(shape_tbl).where(shape_tbl.c.deleted_at.is_(None))  # type: ignore
    res = conn.execute(stmt)
    return [schemas.GeoShape.from_orm(g) for g in res]


def create_shape(
    conn: Connection, geoshape: schemas.GeoShapeCreate
) -> schemas.GeoShape:
    """Create a new shape."""
    ins = (
        insert(shape_tbl)  # type: ignore
        .values(
            created_by_user_id=func.app_user_id(),
            updated_by_user_id=func.app_user_id(),
            updated_at=func.now(),
            created_at=func.now(),
            organization_id=func.app_user_org(),
            name=geoshape.name,
            geojson=geoshape.geojson.json(),
        )
        .returning(shape_tbl)  # type: ignore
    )
    new_shape = conn.execute(ins).fetchone()
    res = schemas.GeoShape.from_orm(new_shape)
    return res


def create_many_shapes(
    conn: Connection, geoshapes: Sequence[schemas.GeoShapeCreate]
) -> List[UUID]:
    """Create many new shapes."""
    ins = (
        insert(shape_tbl)  # type: ignore
        .values(
            created_by_user_id=func.app_user_id(),
            created_at=func.now(),
            updated_by_user_id=func.app_user_id(),
            updated_at=func.now(),
            organization_id=func.app_user_org(),
        )
        .returning(shape_tbl.c.uuid)
    )
    new_shapes = conn.execute(
        ins, [{"name": s.name, "geojson": s.geojson.json()} for s in geoshapes]
    )
    return list(new_shapes)


def update_shape(
    conn: Connection, geoshape: schemas.GeoShapeUpdate
) -> schemas.GeoShape:
    """Update a shape with additional information."""
    values = {
        "name": geoshape.name,
        "updated_at": datetime.datetime.now(),
        "updated_by_user_id": func.app_user_id(),
    }
    if geoshape.geojson:
        values["geojson"] = geoshape.geojson.json()
    stmt = (
        update(shape_tbl)  # type: ignore
        .values(**values)
        .where(shape_tbl.c.uuid == str(geoshape.uuid))
        .returning(shape_tbl)  # type: ignore
    )
    res = conn.execute(stmt)
    rows = res.rowcount
    if rows == 0:
        raise Exception("No rows updated")
    shape = res.fetchone()
    return schemas.GeoShape.from_orm(shape)


def delete_shape(conn: Connection, uuid: UUID) -> Optional[schemas.GeoShape]:
    """Delete a shape."""
    # TODO: What to do if exists?
    values = {
        "deleted_at": datetime.datetime.now(),
        "deleted_by_user_id": func.app_user_id(),
    }
    stmt = (
        update(shape_tbl)
        .values(**values)
        .where(shape_tbl.c.uuid == str(uuid))
        .returning(shape_tbl)
    )
    res = conn.execute(stmt)
    rows = res.rowcount
    if rows == 0:
        raise Exception("No rows updated")
    return schemas.GeoShape.from_orm(res.fetchone())


def delete_many_shapes(conn: Connection, uuids: Sequence[UUID]) -> int:
    """Delete a shape."""
    # TODO: What to do if exists?
    values = {
        "deleted_at": datetime.datetime.now(),
        "deleted_by_user_id": func.app_user_id(),
    }
    stmt = (
        update(shape_tbl).values(**values).where(shape_tbl.c.uuid.in_(uuids))
    )  # type: ignore
    res = conn.execute(stmt)
    rows = res.rowcount
    return rows
