"""IMPORTANT: There are database triggers that affect this logic, see Alembic"""
import datetime
from typing import Union

from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.engine import Connection

from app import models, schemas
from app.core.config import get_settings


class NoUserException(Exception):
    pass


class NoUserWithIdException(NoUserException):
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    def __str__(self) -> str:
        return f"No user with user_id={self.user_id}"


class NoUserWithEmailException(NoUserException):
    def __init__(self, email: str) -> None:
        self.email = email

    def __str__(self) -> str:
        return f"No user with email='{self.email}'"


class NoUserWithSubIdException(NoUserException):
    def __init__(self, sub_id: str) -> None:
        self.sub_id = sub_id

    def __str__(self) -> str:
        return f"No user with sub_id='{self.sub_id}'"


def get_db_user(db: Session, user_id: int) -> models.User:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise NoUserWithIdException(user_id)
    return user


def get_user_by_email(db: Session, email: str) -> schemas.User:
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise NoUserWithEmailException(email)
    return schemas.User(
        **user.__dict__,
    )


def get_user_by_sub_id(db: Session, sub_id: str) -> models.User:
    user = db.query(models.User).filter(models.User.sub_id == sub_id).first()
    if not user:
        raise NoUserWithSubIdException(sub_id)
    return user


def create_user(db: Session, user: schemas.UserCreate) -> schemas.User:
    db_user = models.User(
        sub_id=user.sub_id,
        email=user.email,
        given_name=user.given_name,
        family_name=user.family_name,
        nickname=user.nickname,
        name=user.name,
        picture=user.picture,
        locale=user.locale,
        updated_at=user.updated_at,
        email_verified=user.email_verified,
        iss=user.iss,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return schemas.User(
        **db_user.__dict__,
    )


def create_or_update_user_from_bearer_data(
    conn: Union[Connection, Session], auth_jwt_payload: dict
) -> schemas.User:
    values = dict(auth_jwt_payload)  # This is pulled from auth0
    now = datetime.datetime.utcnow()
    values["sub_id"] = values["sub"]
    values["last_login_at"] = now
    settings = get_settings()

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
    row = conn.execute(stmt, params).fetchone()
    out_user = schemas.User.from_orm(row)
    return out_user
