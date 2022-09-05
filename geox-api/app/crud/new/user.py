"""IMPORTANT: There are database triggers that affect this logic, see Alembic"""
import datetime
from typing import Any, Union

from sqlalchemy import insert
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session

from app import models, schemas
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

    stmt = (
        user_tbl.insert()
        .values(**values)
        .on_conflict_do_update(index_elements=["sub_id"], set_={"last_login_at": now})
        .returning(user_tbl)
    )
    row = conn.execute(stmt)
    out_user = schemas.User.from_orm(row)
    return out_user
