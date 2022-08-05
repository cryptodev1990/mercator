import json
from typing import List, Optional, Union

import jinja2 as j2
from cryptography.fernet import Fernet
from pydantic import UUID4
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.crud.user import get_user
from app.schemas.db_credential import PublicDbCredential

from .. import schemas

settings = get_settings()
_key = settings.fernet_encryption_key
cipher_suite = Fernet(_key)


def get_organization_for_user(db: Session, user_id: int) -> Optional[UUID4]:
    user = get_user(db, user_id)
    organization_id = db.query(user.organization_id).first()
    if organization_id is None:
        return None
    return organization_id[0]


def encrypt(plaintext: str) -> str:
    return cipher_suite.encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: bytes) -> str:
    return cipher_suite.decrypt(ciphertext).decode()


def get_conn(
    db: Session, conn_read: schemas.DbCredentialRead
) -> Union[schemas.PublicDbCredential, None]:
    """Read a single database connection by ID

    Only the user's organization can read a connection.
    If the user has no assigned organization, they can only read their own connections.
    """

    user = get_user(db, conn_read.user_id)
    organization_id = user.organization_id

    tmpl = (
        j2.Template(
            """
      SELECT d.id
      , d.name
      , d.is_default
      , d.created_at
      , uc.email AS created_by_user_email
      , uu.updated_at
      , uu.email AS updated_by_user_email
      FROM db_credentials d
      LEFT JOIN users uc
      ON d.created_by_user_id = uc.id
      LEFT JOIN users uu
      ON d.updated_by_user_id = uu.id
      WHERE 1=1
        AND d.id = :id
        {% if organization_id %}
        AND d.organization_id = :organization_id
        {% else %}
        AND d.created_by_user_id = :user_id
        AND d.organization_id IS NULL
        {% endif %}
      """
        ).render(organization_id=organization_id),
    )

    res = db.execute(
        tmpl,
        {
            "id": conn_read.id,
            "user_id": conn_read.user_id,
            "organization_id": organization_id,
        },
    )
    rows = res.mappings().all()
    return schemas.PublicDbCredential(**rows[0]) if res else None


def get_all_connections(
    db: Session, user: schemas.User
) -> List[schemas.PublicDbCredential]:
    """Read all connections for user"""
    organization_id = get_organization_for_user(db, user.id)

    res = db.execute(
        j2.Template(
            """
    SELECT d.id
    , d.name
    , d.is_default
    , d.created_at
    , d.created_by_user_id
    , d.updated_at
    , d.updated_by_user_id
    , d.db_driver
    FROM db_credentials d
    WHERE 1=1
      {% if organization_id %}
      AND d.organization_id = :organization_id
      {% else %}
      AND d.created_by_user_id = :user_id
      AND d.organization_id IS NULL
      {% endif %}
    """
        ).render(organization_id=organization_id),
        {"user_id": user.id, "organization_id": organization_id},
    )
    rows = res.mappings().all()
    return [schemas.PublicDbCredential(**row) for row in rows] if len(rows) > 0 else []


def create_conn_record(
    db: Session, db_credential: schemas.DbCredentialCreate, user_id: int
) -> PublicDbCredential:

    organization_id = get_organization_for_user(db, user_id)

    encrypted_db_user = encrypt(db_credential.db_user)
    encrypted_db_password = encrypt(db_credential.db_password)
    encrypted_db_host = encrypt(db_credential.db_password)
    encrypted_db_port = encrypt(db_credential.db_port)
    encrypted_db_database = encrypt(db_credential.db_database)
    encrypted_db_extras = encrypt(json.dumps(db_credential.db_extras))

    res = db.execute(
        """
      INSERT INTO db_credentials (
        id,
        name,
        is_default,
        created_at,
        created_by_user_id,
        updated_at,
        updated_by_user_id,
        organization_id,
        db_user,
        db_password,
        db_host,
        db_port,
        db_database,
        db_driver,
        db_extras
      )
        VALUES (
          GEN_RANDOM_UUID(),
          :name,
          :is_default,
          NOW(),
          :user_id,
          NOW(),
          :user_id,
          :organization_id,
          :db_user,
          :db_password,
          :db_host,
          :db_port,
          :db_database,
          :db_driver,
          :db_extras
      ) RETURNING name, id, is_default, created_at, created_by_user_id, updated_at, updated_by_user_id, db_driver;
    """,
        {
            "name": db_credential.name,
            "is_default": db_credential.is_default,
            "user_id": user_id,
            "organization_id": organization_id,
            "db_user": encrypted_db_user,
            "db_password": encrypted_db_password,
            "db_host": encrypted_db_host,
            "db_port": encrypted_db_port,
            "db_database": encrypted_db_database,
            "db_driver": db_credential.db_driver,
            "db_extras": encrypted_db_extras,
        },
    )
    db.commit()

    rows = res.mappings().all()
    db_result = schemas.PublicDbCredential(**rows[0])
    return db_result


def get_conn_with_secrets(
    db: Session, conn_read: schemas.DbCredentialRead
) -> Union[schemas.DbCredentialWithCreds, None]:
    """WARNING: This should never be exposed publicly
    This is exclusively for Celery worker use
    """
    res = db.execute(
        """
    SELECT d.id
    , d.db_driver
    , d.db_user AS encrypted_db_user
    , d.db_password AS encrypted_db_password
    , d.db_host AS encrypted_db_host
    , d.db_port AS encrypted_db_port
    , d.db_database AS encrypted_db_database
    , d.db_extras AS encrypted_db_extras
    FROM db_credentials d
    WHERE 1=1
      AND id = :id
    """,
        {"id": conn_read.id},
    )
    rows = res.mappings().all()
    db_result = schemas.EncryptedDbCredentialWithCreds(**rows[0]) if res else None

    if db_result is None:
        return None

    res = schemas.DbCredentialWithCreds(
        id=db_result.id,
        db_driver=db_result.db_driver,
        db_user=decrypt(db_result.encrypted_db_user),
        db_password=decrypt(db_result.encrypted_db_password),
        db_host=decrypt(db_result.encrypted_db_host),
        db_port=decrypt(db_result.encrypted_db_port),
        db_database=decrypt(db_result.encrypted_db_database),
        db_extras=None,
    )
    if db_result.encrypted_db_extras is not None:
        res.db_extras = json.loads(decrypt(db_result.encrypted_db_extras))
    return res


def update_db_conn(
    db: Session, conn_update: schemas.DbCredentialUpdate
) -> schemas.PublicDbCredential:

    organization_id = get_organization_for_user(db, conn_update.user_id)

    update_args = {
        "id": conn_update.id,
        "user_id": conn_update.user_id,
        "organization_id": organization_id,
    }

    if conn_update.db_user is not None:
        update_args["db_user"] = encrypt(conn_update.db_user)
    if conn_update.db_password is not None:
        update_args["db_password"] = encrypt(conn_update.db_password)
    if conn_update.db_host is not None:
        update_args["db_host"] = encrypt(conn_update.db_host)
    if conn_update.db_port is not None:
        update_args["db_port"] = encrypt(conn_update.db_port)
    if conn_update.db_database is not None:
        update_args["db_database"] = encrypt(conn_update.db_database)
    if conn_update.db_extras is not None:
        update_args["db_extras"] = encrypt(json.dumps(conn_update.db_extras))
    if conn_update.is_default is not None:
        update_args["is_default"] = conn_update.is_default
    if conn_update.name is not None:
        update_args["name"] = conn_update.name

    if conn_update.db_driver is not None:
        update_args["db_driver"] = conn_update.db_driver

    update_template = j2.Template(
        """
      UPDATE db_credentials
      SET updated_at = NOW()
      , updated_by_user_id = :user_id
      {% for key, value in update_args.items() %}
        {% if key.startswith('db_') or key in ["is_default", "name"] %}
        , {{key}} = :{{key}}
        {% endif %}
      {% endfor %}
      WHERE id = :id
      {% if update_args.get('organization_id') %}
        AND organization_id = :organization_id
      {% else %}
        AND created_by_user_id = :user_id
      {% endif %}
      RETURNING name, id, is_default, created_at, created_by_user_id, updated_at, updated_by_user_id, db_driver;
      """
    )

    res = db.execute(update_template.render(update_args=update_args), update_args)
    db.commit()
    rows = res.mappings().all()
    db_result = schemas.PublicDbCredential(**rows[0])
    return db_result


def delete_db_conn(db: Session, conn_id: UUID4, user_id: int) -> bool:
    """Delete a database connection

    Users can only delete their own connections or connections that belong to their organization
    If the user does not belong to an organization, they can delete only their own connections

    TODO there's an issue with terminated admin employees here
    """
    organization_id = get_organization_for_user(db, user_id)

    db.execute(
        j2.Template(
            """
    DELETE FROM db_credentials
    WHERE id = :id
    {% if organization_id %}
      AND organization_id = :organization_id
    {% else %}
      AND created_by_user_id = :user_id
    {% endif %}
  """
        ).render(organization_id=organization_id),
        {"id": conn_id, "organization_id": organization_id, "user_id": user_id},
    )
    db.commit()
    return True


def get_num_connections_for_user(db: Session, user_id: int) -> int:
    organization_id = get_organization_for_user(db, user_id)
    res = db.execute(
        j2.Template(
            """
      SELECT COUNT(*) FROM db_credentials
      {% if organization_id %}
        WHERE organization_id = :organization_id
      {% else %}
        WHERE created_by_user_id = :user_id
      {% endif %}
    """
        ).render(organization_id=organization_id),
        {"organization_id": organization_id, "user_id": user_id},
    )
    rows = res.mappings().all()
    return rows[0]["count"]


def get_last_created_connection_for_user(
    db: Session, user_id: int
) -> Optional[schemas.PublicDbCredential]:
    res = db.execute(
        """
      SELECT * FROM db_credentials
      WHERE created_by_user_id = :user_id
      ORDER BY created_at DESC
      LIMIT 1
    """,
        {"user_id": user_id},
    )
    rows = res.mappings().all()
    if not rows:
        return None
    db_result = schemas.PublicDbCredential(**rows[0])
    return db_result
