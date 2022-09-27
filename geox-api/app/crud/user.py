"""IMPORTANT: There are database triggers that affect this logic, see Alembic"""
import datetime
from typing import Any, Union

from sqlalchemy import insert, text
from sqlalchemy.orm import Session

from app import models
from app.core.config import Settings, get_settings
from app.schemas import User


class NoUserException(Exception):
    """No user exists exception."""

    pass


class NoUserWithIdException(NoUserException):
    """No user exists with this id exception."""

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    def __str__(self) -> str:
        return f"No user with user_id={self.user_id}"


def get_user(db: Session, user_id: int) -> User:
    stmt = text(
        """
    SELECT *
    FROM user
    WHERE user_id = :user_id
    """
    )
    user = db.execute(stmt, {"user_id": user_id}).first()
    if user is None:
        raise NoUserWithIdException(user_id)
    return User.from_orm(user)


def create_or_update_user_from_bearer_data(
    db: Session, auth_jwt_payload: dict, settings: Settings = get_settings()
) -> User:
    values = dict(auth_jwt_payload)  # This is pulled from auth0
    now = datetime.datetime.utcnow()
    values["sub_id"] = values["sub"]
    values["last_login_at"] = now

    # Handling the special case of machine account
    # this should be created as the first value anyways
    if values["sub"] == settings.machine_account_sub_id:
        values["email"] = settings.machine_account_email

    stmt = text(
        """
        INSERT INTO users
        (sub_id, email, is_active, given_name, family_name, nickname, name, picture, locale, updated_at, email_verified, iss, last_login_at)
        VALUES
        (:sub_id, :email, TRUE, :given_name, :family_name, :nickname, :name, :picture, :locale, :updated_at, :email_verified, :iss, :last_login_at)
        ON CONFLICT (sub_id)
        DO UPDATE
        SET last_login_at = :last_login_at
        RETURNING *
        """
    )
    cols = (
        "sub_id",
        "email",
        "is_active",
        "given_name",
        "family_name",
        "nickname",
        "name",
        "picture",
        "locale",
        "updated_at",
        "email_verified",
        "iss",
        "last_login_at",
    )
    params = {c: values.get(c) for c in cols}
    row = db.execute(stmt, params).fetchone()
    out_user = User.from_orm(row)
    return out_user
