"""IMPORTANT: There are database triggers that affect this logic, see Alembic"""
import datetime

from sqlalchemy import text
from sqlalchemy.engine import Connection

from app import schemas
from app.core.config import get_settings
from app.models import User

user_tbl = User.__table__


def create_or_update_user_from_bearer_data(
    conn: Connection, auth_jwt_payload: dict
) -> schemas.User:
    values = dict(auth_jwt_payload)  # This is pulled from auth0
    now = datetime.datetime.utcnow()
    values["sub_id"] = values["sub"]
    values["last_login_at"] = now
    settings = get_settings()

    if values["sub"] == settings.machine_account_sub_id:
        values["email"] = settings.machine_account_email

    stmt = text("""
    INSERT INTO users
    (sub_id, email, is_active, given_name, family_name, nickname, name, picture, locale, updated_at, email_verified, iss, last_login_at)
    VALUES
    (:sub_id, :email, TRUE, :given_name, :family_name, :nickname, :name, :picture, :locale, :updated_at, :email_verified, :iss, :last_login_at)
    ON CONFLICT (sub_id)
    DO UPDATE
    SET last_login_at = :last_login_at
    RETURNING *
    """)
    cols = ("sub_id", "email", "is_active", "given_name", "family_name", "nickname", "name", "picture", "locale", "updated_at", "email_verified", "iss", "last_login_at")
    params = {c: values.get(c) for c in cols}
    row = conn.execute(stmt, params).fetchone()
    out_user = schemas.User.from_orm(row)
    return out_user
