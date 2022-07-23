import jinja2
import datetime
import json
from typing import List, Optional, Union
from pydantic import UUID4

from sqlalchemy.orm import Session

from .. import schemas


def get_shape(
    db: Session, shape: schemas.GeoShapeRead
) -> Union[schemas.GeoShape, None]:
    res = db.execute(
        """
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
    """,
        {"uuid": shape.uuid},
    )
    rows = res.mappings().all()
    return schemas.GeoShape(**rows[0]) if res else None


def get_all_shapes_by_user(db: Session, user: schemas.User) -> List[schemas.GeoShape]:
    res = db.execute(
        """
        SELECT shapes.uuid::VARCHAR AS uuid
        , shapes.name
        , shapes.geojson
        , shapes.created_at
        , shapes.created_by_user_id
        FROM shapes
        JOIN users
        ON users.id = shapes.created_by_user_id
          AND users.id = :user_id
        WHERE 1=1
          AND shapes.deleted_at IS NULL
        """,
        {"user_id": user.id},
    )
    rows = res.mappings().all()
    return [schemas.GeoShape(**row) for row in rows] if len(rows) > 0 else []


def get_all_shapes_by_email_domain(
    db: Session, email_domain: str
) -> List[schemas.GeoShape]:
    res = db.execute(
        """
        SELECT shapes.uuid::VARCHAR AS uuid
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
        ORDER BY created_at DESC
        """,
        {"email_domain_wildcard": f"%@{email_domain}"},
    )
    rows = res.mappings().all()
    return [schemas.GeoShape(**row) for row in rows] if len(rows) > 0 else []


def create_shape(
    db: Session, geoshape: schemas.GeoShapeCreate, user_id: int
) -> schemas.GeoShape:
    now = datetime.datetime.utcnow()
    res = db.execute(
        """
    INSERT INTO shapes (uuid, name, geojson, created_at, created_by_user_id, updated_at, updated_by_user_id)
        VALUES (GEN_RANDOM_UUID(), :name, :geojson, :now, :created_by_user_id, :now, :created_by_user_id)
        RETURNING uuid;
    """,
        {
            # TODO This is needlessly slow
            "geojson": geoshape.geojson.json(),
            "name": geoshape.name,
            "created_by_user_id": user_id,
            "now": now,
        },
    )
    db.commit()
    rows = res.mappings().all()
    uuid = rows[0]["uuid"]
    new_shape = schemas.GeoShape(
        name=geoshape.name,
        uuid=uuid,
        geojson=geoshape.geojson,
        created_by_user_id=user_id,
        created_at=now,
        updated_at=now,
        updated_by_user_id=user_id,
    )
    return new_shape


def update_shape(
    db: Session, geoshape: schemas.GeoShapeUpdate, user_id: int
) -> Optional[schemas.GeoShape]:
    db_shape = get_shape(db, schemas.GeoShapeRead(uuid=geoshape.uuid))
    if db_shape is None:
        raise Exception(f"Shape {geoshape.uuid} not found")
    db_shape.geojson = (
        json.loads(geoshape.geojson.json()
                   ) if geoshape.geojson else db_shape.geojson
    )
    db_shape.name = geoshape.name or db_shape.name
    deleted_at, deleted_at_by_user_id = None, None
    if geoshape.should_delete:
        deleted_at_by_user_id = user_id
        deleted_at = datetime.datetime.utcnow()

    res = db.execute(
        """
    UPDATE shapes
      SET geojson = :geojson
      , name = :name
      , updated_at = :now
      , updated_by_user_id = :updated_by_user_id
      , deleted_at = :deleted_at
      , deleted_at_by_user_id = :deleted_at_by_user_id
      WHERE 1=1
        AND uuid = :uuid
      RETURNING *
    """,
        {
            "uuid": db_shape.uuid,
            # TODO This is needlessly slow
            "geojson": json.dumps(
                db_shape.geojson
                if type(db_shape.geojson) is dict
                else db_shape.geojson.json()
            ),
            "name": db_shape.name,
            "now": datetime.datetime.utcnow(),
            "updated_by_user_id": user_id,
            "deleted_at": deleted_at,
            "deleted_at_by_user_id": deleted_at_by_user_id,
        },
    )
    db.commit()
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


def bulk_create_shapes(
    db: Session, geoshapes: List[schemas.GeoShapeCreate], user_id: int
) -> schemas.ShapeCountResponse:
    now = datetime.datetime.utcnow()
    interpolated_dict = {}
    insertable = ""
    for i, geoshape in enumerate(geoshapes):
        interpolated_dict[f"geojson_{i}"] = geoshape.geojson.json()
        interpolated_dict[f"name_{i}"] = geoshape.name
        comma = ',' if i != len(geoshapes) - 1 else ''
        insertable += f'(GEN_RANDOM_UUID(), :name_{i}, :geojson_{i}, :now, :user_id, :now, :user_id)' + comma
    db.execute(f"""INSERT INTO shapes (
        uuid, name, geojson, created_at, created_by_user_id, updated_at, updated_by_user_id)
    VALUES {insertable}
    """,
    {
        **interpolated_dict,
        "user_id": user_id,
        "now": now,
    })
    db.commit()
    res = db.execute(
        """SELECT COUNT(*) AS num_shapes
        FROM shapes
        WHERE 1=1
          AND created_by_user_id = :user_id
          AND created_at BETWEEN :transaction_time AND NOW() AT TIME ZONE 'UTC'""",
        {"user_id": user_id, "transaction_time": now})
    rows = res.mappings().all()
    return rows[0]


def bulk_soft_delete_shapes(
    db: Session, shape_uuids: List[UUID4], user_id: int
) -> schemas.ShapeCountResponse:
    now = datetime.datetime.utcnow()
    db.execute("""UPDATE shapes
        SET deleted_at = :now
        , updated_by_user_id = :user_id
        WHERE uuid IN :uuid_list
          -- You can't delete shapes if you're not part of the same domain
          AND created_by_user_id IN (
            SELECT users.id
            FROM users
            JOIN (
                SELECT SUBSTRING(email FROM '@(.*)$') AS domain
                FROM users
                WHERE id = :user_id
            ) domain_filter
            ON SUBSTRING(users.email FROM '@(.*)$') = domain_filter.domain
          )
    """,
               {
                   "uuid_list": tuple(str(guid) for guid in shape_uuids),
                   "now": now,
                   "user_id": user_id
               },
               )
    db.commit()
    res = db.execute(
        """SELECT COUNT(*) AS num_shapes
        FROM shapes
        WHERE 1=1
          AND updated_by_user_id = :user_id
          AND deleted_at BETWEEN :transaction_time AND NOW() AT TIME ZONE 'UTC'""",
        {"user_id": user_id, "transaction_time": now})
    rows = res.mappings().all()
    return schemas.ShapeCountResponse(**rows[0])
