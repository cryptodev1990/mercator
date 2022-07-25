import datetime
from typing import Union

from sqlalchemy.orm import Session

from app import models, schemas
from app.core.config import get_settings

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


def get_user(db: Session, user_id: int) -> models.User:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise NoUserWithIdException(user_id)
    return user


def get_user_by_email(db: Session, email: str) -> models.User:
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise NoUserWithEmailException(email)
    return user


def get_user_by_sub_id(db: Session, sub_id: str) -> models.User:
    user = db.query(models.User).filter(models.User.sub_id == sub_id).first()
    if not user:
        raise NoUserWithSubIdException(sub_id)
    return user


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def update_user_by_email(db: Session, user: UserType) -> models.User:
    if not user.email:
        raise ValueError("Missing email")
    db_user = get_user_by_email(db, user.email)
    if not db_user:
        raise Exception(f"no user with email {user.email}")
    db_user.last_login_at = user.last_login_at  # type: ignore
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_by_id(db: Session, user: UserType) -> models.User:
    if not user.id:
        raise ValueError("Missing user_id")
    db_user = get_user(db, user.id)
    if not db_user:
        raise Exception(f"no user with id {user.id}")
    db_user.last_login_at = user.last_login_at  # type: ignore
    db.commit()
    db.refresh(db_user)
    return db_user


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
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
    return db_user


def handle_management_api_account(user, db):
    now = datetime.datetime.utcnow()
    new_user = create_user(
        db,
        models.User(
            sub_id=user["sub"],
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
) -> models.User:
    user = dict(auth_jwt_payload)
    try:
        existing_user = get_user_by_sub_id(db, user["sub"])
    except NoUserException:
        existing_user = None
    now = datetime.datetime.utcnow()
    user["last_login_at"] = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    out_user: models.User
    if existing_user:
        existing_user.last_login_at = now
        out_user = update_user_by_id(db, existing_user)
    elif is_management(user):
        out_user = handle_management_api_account(user, db)
    else:
        out_user = create_user(
            db,
            schemas.UserCreate(
                sub_id=user["sub"],
                email=user["email"],
                given_name=user.get("given_name"),
                family_name=user.get("family_name"),
                nickname=user["nickname"],
                name=user.get("name"),
                picture=user.get("picture"),
                locale=user.get("locale"),
                updated_at=user["updated_at"],
                email_verified=user["email_verified"],
                iss=user["iss"],
                last_login_at=now,
            ),
        )
    return out_user
