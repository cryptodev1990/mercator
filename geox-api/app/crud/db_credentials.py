import json
from typing import List, Optional, Union

import jinja2 as j2
from cryptography.fernet import Fernet
from pydantic import UUID4
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.crud.organization import get_active_org
from app.schemas.db_credential import PublicDbCredential

from .. import models, schemas

settings = get_settings()
_key = settings.fernet_encryption_key
cipher_suite = Fernet(_key)


class DbCredentialModelException(Exception):
    pass


def encrypt(plaintext: str) -> str:
    return cipher_suite.encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: bytes) -> str:
    return cipher_suite.decrypt(ciphertext).decode()


def get_conn(
    db: Session, user_id: int, db_credential_id: UUID4
) -> schemas.PublicDbCredential:
    """Read a single database connection by ID

    Only the user's organization can read a connection.
    """
    organization_id = get_active_org(db, user_id)

    if not organization_id:
        raise DbCredentialModelException("User has no organization")

    connection = (
        db.query(models.DbCredential)
        .filter(
            models.DbCredential.id == db_credential_id,
            models.DbCredential.organization_id == organization_id,
        )
        .first()
    )

    if not connection:
        raise DbCredentialModelException("Connection not found")

    return PublicDbCredential(**connection.__dict__)


def get_conns(db: Session, user: schemas.User) -> List[schemas.PublicDbCredential]:
    """Read all connections for user"""
    organization_id = get_active_org(db, user.id)
    if not organization_id:
        raise DbCredentialModelException("User has no organization")

    connections = (
        db.query(models.DbCredential)
        .filter(models.DbCredential.organization_id == organization_id)
        .all()
    )
    return [schemas.PublicDbCredential(**row.__dict__) for row in connections]


def create_conn(
    db: Session, db_credential: schemas.DbCredentialCreate, user_id: int
) -> PublicDbCredential:

    org_id = get_active_org(db, user_id)

    encrypted_db_user = encrypt(db_credential.db_user)
    encrypted_db_password = encrypt(db_credential.db_password)
    encrypted_db_host = encrypt(db_credential.db_password)
    encrypted_db_port = encrypt(db_credential.db_port)
    encrypted_db_database = encrypt(db_credential.db_database)
    encrypted_db_extras = encrypt(json.dumps(db_credential.db_extras))

    cred = models.DbCredential(
        name=db_credential.name,
        organization_id=org_id,
        is_default=db_credential.is_default,
        created_by_user_id=user_id,
        updated_by_user_id=user_id,
        db_driver=db_credential.db_driver,
        db_user=encrypted_db_user,
        db_password=encrypted_db_password,
        db_host=encrypted_db_host,
        db_port=encrypted_db_port,
        db_database=encrypted_db_database,
        db_extras=encrypted_db_extras,
    )
    db.add(cred)
    db.commit()
    db.refresh(cred)
    return PublicDbCredential(**cred.__dict__)


def get_conn_secrets(
    db: Session, db_credential_id: UUID4
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
    , d.name
    FROM db_credentials d
    WHERE 1=1
      AND id = :id
    """,
        {"id": db_credential_id},
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
        name=db_result.name,
        db_extras=None,
    )
    if db_result.encrypted_db_extras is not None:
        res.db_extras = json.loads(decrypt(db_result.encrypted_db_extras))
    return res


def update_conn(
    db: Session, conn_update: schemas.DbCredentialUpdate, user_id: int
) -> schemas.PublicDbCredential:

    organization_id = get_active_org(db, user_id)

    if not organization_id:
        raise DbCredentialModelException("User does not have an organization")

    conn = get_conn(db, db_credential_id=conn_update.id, user_id=user_id)
    if not conn:
        raise DbCredentialModelException("Connection not found")

    if conn.organization_id != organization_id:
        raise DbCredentialModelException(
            "User does not have permission to update this connection"
        )

    update_args = {
        "id": conn_update.id,
        "user_id": user_id,
        "organization_id": organization_id,
    }

    suggested_updates = conn_update.dict(exclude_unset=True)

    for key in suggested_updates:
        if key in ("db_user", "db_password", "db_host", "db_port", "db_database"):
            update_args[key] = encrypt(suggested_updates[key])
        elif key == "db_extras":
            update_args["db_extras"] = encrypt(json.dumps(suggested_updates[key]))
        else:
            update_args[key] = suggested_updates[key]

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
        AND organization_id = :organization_id
      RETURNING name, id, is_default, created_at, created_by_user_id, updated_at, updated_by_user_id, db_driver;
      """
    )

    res = db.execute(update_template.render(update_args=update_args), update_args)
    db.commit()
    rows = res.mappings().all()
    db_result = schemas.PublicDbCredential(**rows[0])
    return db_result


def delete_conn(db: Session, conn_id: UUID4, user_id: int) -> int:
    """Delete a database connection

    Users can only delete connections that belong to their organization

    Returns number of affected rows
    """

    organization_id = get_active_org(db, user_id)
    if not organization_id:
        raise DbCredentialModelException("User does not have an organization")

    conn = get_conn(db, db_credential_id=conn_id, user_id=user_id)
    if not conn:
        raise DbCredentialModelException("Connection not found")

    if conn.organization_id != organization_id:
        raise DbCredentialModelException(
            "User does not have permission to delete this connection"
        )

    num_conns = count_conns(db, user_id)
    db.query(models.DbCredential).filter_by(
        id=str(conn_id), organization_id=organization_id
    ).delete()
    db.commit()
    new_num_conns = count_conns(db, user_id)
    return new_num_conns - num_conns


def count_conns(db: Session, user_id: int) -> int:
    organization_id = get_active_org(db, user_id)
    res = db.execute(
        j2.Template(
            """
      SELECT COUNT(*) AS freq FROM db_credentials
        WHERE organization_id = :organization_id
    """
        ).render(organization_id=organization_id),
        {"organization_id": organization_id, "user_id": user_id},
    )
    rows = res.mappings().all()
    return rows[0]["freq"]


def get_mru_conn(db: Session, user_id: int) -> Optional[schemas.PublicDbCredential]:
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
