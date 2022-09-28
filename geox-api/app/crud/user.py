"""IMPORTANT: There are database triggers that affect this logic, see Alembic."""
import datetime
from typing import Optional, Union

from app.core.config import Settings, get_settings
from app.schemas import User
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session


class NoUserException(Exception):
    """No user exists exception."""

    pass


class NoUserWithIdException(NoUserException):
    """No user exists with this id exception."""

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    def __str__(self) -> str:
        return f"No user with user_id={self.user_id}"


def get_user(db: Union[Session, Connection], user_id: int) -> User:
    stmt = text(
        """
    SELECT *
    FROM users
    WHERE user_id = :user_id
    """
    )
    user = db.execute(stmt, {"user_id": user_id}).first()
    if user is None:
        raise NoUserWithIdException(user_id)
    return User.from_orm(user)

def get_user_by_sub_id(db: Union[Session, Connection], sub_id: str) -> Optional[User]:
    """Get a user by their Auth0 `sub_id`.

    Returns:
        A user object if the user exists, and `None` if they do not.
    """
    stmt = text(
        """
    SELECT *
    FROM users
    WHERE sub_id = :sub_id
    """
    )
    user = db.execute(stmt, {"sub_id": sub_id}).first()
    return User.from_orm(user) if user else None

def create_or_update_user_from_bearer_data(
    db: Union[Session, Connection], auth_jwt_payload: dict, settings: Settings = get_settings()
) -> User:
    values = dict(auth_jwt_payload)  # This is pulled from auth0
    now = datetime.datetime.utcnow()
    values["sub_id"] = values["sub"]
    values["last_login_at"] = now

    # Handling the special case of machine account
    # this should be created as the first value anyways
    if values["sub"] == settings.machine_account_sub_id:
        values["email"] = settings.machine_account_email

    # see if user exists
    existing_user = get_user_by_sub_id(db, values["sub_id"])
    if existing_user:
        return User.from_orm(existing_user)
    # try to insert
    ins_stmt = """
        INSERT INTO users
        (sub_id, email, is_active, given_name, family_name, nickname, name, picture, locale, updated_at, email_verified, iss)
        VALUES
        (:sub_id, :email, TRUE, :given_name, :family_name, :nickname, :name, :picture, :locale, :updated_at, :email_verified, :iss)
        ON CONFLICT (sub_id) DO NOTHING
        RETURNING *
        """
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
    )
    params = {c: values.get(c) for c in cols}
    new_user = db.execute(ins_stmt, params).first()
    # try again if race condition
    if not new_user:
        new_user = get_user_by_sub_id(db, values["sub_id"])
    return User.from_orm(new_user)
