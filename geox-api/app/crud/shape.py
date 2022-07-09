import datetime
import json
from typing import List, Union, Optional

from sqlalchemy.orm import Session

from .. import models, schemas


def get_shape(
    db: Session, shape: schemas.GeoShapeRead
) -> Union[schemas.GeoShape, None]:
    res = db.execute("""
    SELECT uuid
    , name
    , created_at
    , created_by_user_id
    , deleted_at
    , deleted_at_by_user_id
    , geojson
    FROM shapes
    WHERE 1=1
      AND deleted_at IS NULL
      AND uuid = :uuid
    LIMIT 1
    """, {"uuid": shape.uuid})
    rows = res.mappings().all()
    return schemas.GeoShape(**rows[0]) if res else None


def get_all_shapes_by_user(db: Session, user: schemas.User) -> List[schemas.GeoShape]:
    return (
        db.query(models.Shape).filter(
            models.Shape.created_by_user_id == user.id, models.Shape.deleted_at.is_(None)).all()
    )


def get_all_shapes_by_email_domain(
    db: Session, email_domain: str
) -> List[schemas.GeoShape]:
    res = db.execute(
        """
        SELECT shapes.uuid
        , shapes.name
        , shapes.geojson
        , shapes.created_at
        , shapes.created_by_user_id
        FROM shapes
        JOIN users
        ON users.id = shapes.created_by_user_id
          AND users.email LIKE :email_domain_wildcard
        WHERE 1=1
          AND shapes.deleted_at IS NULL
        """,
        {"email_domain_wildcard": f'%@{email_domain}'},
    )
    rows = res.mappings().all()
    return [schemas.GeoShape(**row) for row in rows] if len(rows) > 0 else []


def create_shape(db: Session, geoshape: schemas.GeoShapeCreate, user_id: int):
    db_shape = models.Shape(
        # TODO This is needlessly slow
        geojson=json.loads(geoshape.geojson.json()),
        name=geoshape.name,
        created_by_user_id=user_id
    )
    db.add(db_shape)
    db.commit()
    db.refresh(db_shape)
    return db_shape


def update_shape(db: Session, geoshape: schemas.GeoShapeUpdate, user_id: int) -> Optional[schemas.GeoShape]:
    db_shape = get_shape(db, schemas.GeoShapeRead(uuid=geoshape.uuid))
    if db_shape is None:
        raise Exception(f"Shape {geoshape.uuid} not found")
    db_shape.geojson = json.loads(geoshape.geojson.json()) if geoshape.geojson else db_shape.geojson
    db_shape.name = geoshape.name or db_shape.name
    deleted_at, deleted_at_by_user_id = None, None
    if geoshape.should_delete:
        deleted_at_by_user_id = user_id
        deleted_at = datetime.datetime.now()

    res = db.execute("""
    UPDATE shapes
      SET geojson = :geojson
      , name = :name
      , updated_at = NOW()
      , updated_by_user_id = :updated_by_user_id
      , deleted_at = :deleted_at
      , deleted_at_by_user_id = :deleted_at_by_user_id
      WHERE 1=1
        AND uuid = :uuid
      RETURNING *
    """, {
        "uuid": db_shape.uuid,
        # TODO This is needlessly slow
        "geojson": json.dumps(db_shape.geojson if type(db_shape.geojson) is dict else db_shape.geojson.json()),
        "name": db_shape.name,
        "updated_by_user_id": user_id,
        "deleted_at": deleted_at,
        "deleted_at_by_user_id": deleted_at_by_user_id
    })
    if geoshape.should_delete:
        return None
    rows = res.mappings().all()
    return schemas.GeoShape(**rows[0])


def hard_delete_shape(db: Session, geoshape: schemas.GeoShape):
    db_shape = get_shape(db, schemas.GeoShapeRead(uuid=geoshape.uuid))
    if db_shape is None:
        raise Exception(f"Shape {geoshape.uuid} not found")
    db.delete(db_shape)
    return db_shape