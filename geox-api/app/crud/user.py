"""IMPORTANT: There are database triggers that affect this logic, see Alembic"""
import datetime
from typing import Any, Union

from sqlalchemy import insert
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.config import get_settings
from app.models import User

UserType = Union[schemas.User, models.User]


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


def get_user(db: Session, user_id: int) -> schemas.User:
    db_user = get_db_user(db, user_id)
    return schemas.User(**db_user.__dict__)


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


def update_user_by_id(db: Session, user: UserType) -> models.User:
    if not user.id:
        raise ValueError("Missing user_id")
    user_id: Any = user.id
    db_user = get_db_user(db, user_id)
    if not db_user:
        raise Exception(f"no user with id {user.id}")
    db_user.last_login_at = user.last_login_at  # type: ignore
    db.commit()
    db.refresh(db_user)
    return db_user


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


def handle_management_api_account(user, db) -> schemas.User:
    now = datetime.datetime.utcnow()
    new_user = create_user(
        db,
        models.User(
            sub_id=get_settings().machine_account_sub_id,
            email="duber+ManagementApi@mercator.tech",
            iss=user["iss"],
            last_login_at=now,
        ),
    )
    return new_user


def is_management(user: dict) -> bool:
    return user["sub"] == get_settings().machine_account_sub_id


def create_or_update_user_from_bearer_data(
    db: Session, auth_jwt_payload: dict
) -> schemas.User:
    user_auth_dict = dict(auth_jwt_payload)  # This is pulled from auth0
    out_user: schemas.User
    existing_user: models.User
    now = datetime.datetime.utcnow()

    try:
        existing_user = get_user_by_sub_id(db, user_auth_dict["sub"])
        existing_user.last_login_at = now  # type: ignore
        updated_user = update_user_by_id(db, existing_user)
        out_user = schemas.User(**updated_user.__dict__)
    except NoUserException:
        user_auth_dict["last_login_at"] = now.strftime("%Y-%m-%d %H:%M:%S.%f")
        user_auth_dict["sub_id"] = user_auth_dict["sub"]
        if is_management(user_auth_dict):
            out_user = handle_management_api_account(user_auth_dict, db)
            return out_user
        out_user = create_user(
            db,
            schemas.UserCreate(
                **user_auth_dict,
            ),
        )
    return out_user


def delete_user(db: Session, user_id: int) -> None:
    db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()


def delete_user_by_email(db: Session, email: str) -> None:
    db.query(models.User).filter(models.User.email == email).delete()
    db.commit()
