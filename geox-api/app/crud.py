import datetime

from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_sub_id(db: Session, sub: str):
    return db.query(models.User).filter(models.User.sub_id == sub).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def update_user_by_email(db: Session, user: schemas.User):
    db_user = get_user_by_email(db, user.email)
    if not db_user:
        raise Exception(f"no user with email {user.email}")
    db_user.last_login_at = user.last_login_at
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_by_id(db: Session, user: schemas.User):
    db_user = get_user_by_email(db, user.email)
    if not db_user:
        raise Exception(f"no user with id {user.id}")
    db_user.last_login_at = user.last_login_at
    db.commit()
    db.refresh(db_user)
    return db_user


def create_user(db: Session, user: schemas.UserCreate):
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


def create_or_update_user_from_bearer_data(db: Session, auth_jwt_payload: dict):
    user = dict(auth_jwt_payload)
    existing_user = get_user_by_sub_id(db, user['sub'])
    now = datetime.datetime.utcnow()
    user['last_login_at'] = now.strftime(
        '%Y-%m-%d %H:%M:%S.%f')
    if existing_user:
        existing_user.last_login_at = now
        update_user_by_id(db, existing_user)
    else:
        new_user = create_user(db, models.User(
            sub_id=user['sub'],
            email=user['email'],
            given_name=user.get('given_name'),
            family_name=user.get('family_name'),
            nickname=user['nickname'],
            name=user.get('name'),
            picture=user.get('picture'),
            locale=user.get('locale'),
            updated_at=user['updated_at'],
            email_verified=user['email_verified'],
            iss=user['iss'],
            last_login_at=now
        ))