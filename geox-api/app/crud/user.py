"""IMPORTANT: There are database triggers that affect this logic, see Alembic."""
import datetime
from typing import Optional

from sqlalchemy import insert, text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError

from app.core.config import Settings, get_settings
from app.db.metadata import users as users_tbl
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


class NoUserWithSubIdException(NoUserException):
    """No user exists with this sub id exception."""

    def __init__(self, sub_id: str) -> None:
        self.sub_id = sub_id

    def __str__(self) -> str:
        return f"No user with sub_id={self.sub_id}"


class NoUserWithEmailException(NoUserException):
    """No user exists with this sub id exception."""

    def __init__(self, sub_id: str) -> None:
        self.sub_id = sub_id

    def __str__(self) -> str:
        return f"No user with email={self.sub_id}"


class UserExistsError(Exception):
    """User already exists with this sub id exception."""

    # Usage of this would need extra info in different contexts
    # to determine who the existing user is.

    def __str__(self) -> str:
        return "User exists."


def get_user(conn: Connection, user_id: int) -> User:
    """Get user by Id.

    Raises:
        NoUserWithIdException: If user doesn't exist.
    """
    stmt = text(
        """
    SELECT *
    FROM users
    WHERE user_id = :user_id
    """
    )
    user = conn.execute(stmt, {"user_id": user_id}).first()
    if user is None:
        raise NoUserWithIdException(user_id)
    return User.from_orm(user)


def get_user_by_sub_id(conn: Connection, sub_id: str) -> User:
    """Get a user by their Auth0 `sub_id`.

    Returns:
        A user object if the user exists, and `None` if they do not.
    Raises:
        NoUserWithSubIdException: If user doesn't exist.
    """
    stmt = text(
        """
    SELECT *
    FROM users
    WHERE sub_id = :sub_id
    """
    )
    user = conn.execute(stmt, {"sub_id": sub_id}).first()
    if user is None:
        raise NoUserWithSubIdException(sub_id)
    return User.from_orm(user)


def get_user_by_email(conn: Connection, email: str) -> User:
    """Get a user by their email.

    Returns:
        A user object if the user exists, and `None` if they do not.

    Raises:
        NoUserWithEmailException: If user doesn't exist.
    """
    stmt = text(
        """
    SELECT *
    FROM users
    WHERE email = :email
    """
    )
    user = conn.execute(stmt, {"email": email}).first()
    if user is None:
        raise NoUserWithEmailException(email)
    return User.from_orm(user)


def create_user(
    conn: Connection,
    *,
    email: str,
    sub_id: str,
    name: Optional[str] = None,
    nickname: Optional[str] = None,
    family_name: Optional[str] = None,
    updated_at: Optional[datetime.datetime] = None,
    iss: Optional[str] = None,
    email_verified: Optional[bool] = False,
    picture: Optional[str] = None,
    locale: Optional[str] = None,
    is_active: bool = True,
) -> User:
    stmt = insert(users_tbl).returning(users_tbl)
    try:
        res = conn.execute(
            stmt,
            {
                "email": email,
                "sub_id": sub_id,
                "name": name,
                "nickname": nickname,
                "family_name": family_name,
                "updated_at": updated_at,
                "iss": iss,
                "email_verified": email_verified,
                "locale": locale,
                "picture": picture,
                "is_active": is_active,
            },
        ).first()
    except IntegrityError:
        raise UserExistsError()
    return User.from_orm(res)


def create_or_update_user_from_bearer_data(
    conn: Connection, auth_jwt_payload: dict, settings: Settings = get_settings()
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
    existing_user = get_user_by_sub_id(conn, values["sub_id"])
    if existing_user:
        return User.from_orm(existing_user)
    # try to insert
    ins_stmt = text(
        """
        INSERT INTO users
        (sub_id, email, is_active, given_name, family_name, nickname, name, picture, locale, updated_at, email_verified, iss)
        VALUES
        (:sub_id, :email, TRUE, :given_name, :family_name, :nickname, :name, :picture, :locale, :updated_at, :email_verified, :iss)
        ON CONFLICT (sub_id) DO NOTHING
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
    )
    params = {c: values.get(c) for c in cols}
    new_user = conn.execute(ins_stmt, params).first()
    # try again if race condition
    if not new_user:
        new_user = get_user_by_sub_id(conn, values["sub_id"])
    return User.from_orm(new_user)
