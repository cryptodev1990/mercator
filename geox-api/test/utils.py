import datetime
from contextlib import contextmanager
from typing import Any, Generator, List, Tuple

from app import models, schemas
from app.crud.db_credentials import create_conn, delete_conn, get_mru_conn
from app.crud.organization import (
    create_organization,
    create_organization_and_assign_to_user,
    get_org,
    upsert_organization_for_user,
)
from app.crud.user import (
    NoUserWithEmailException,
    create_user,
    delete_user,
    delete_user_by_email,
    get_user_by_email,
)
from app.db.session import SessionLocal

emails = [
    "testuser@mercator.tech",
    "testuser-friendly@mercator.tech",
    "testuser-adversary@mercator.tech",
    "testuser-noorg@mercator.tech",
]


def make_user(db, test_email):
    username = test_email.split("@")[0]
    domain_part = test_email.split("@")[1]
    new_user = schemas.UserCreate(
        email=test_email,
        given_name="Test",
        family_name="User",
        name=username,
        nickname=username,
        email_verified=True,
        iss="https://" + domain_part,
        sub_id=username,
        picture="https://mercator.tech/testuser.png",
        locale="en-US",
        updated_at=datetime.datetime.utcnow(),
    )
    create_user(db, new_user)


def cleanup_test_users(db):
    for email in emails:
        try:

            user = get_user_by_email(db, email)
            user = schemas.User(**user.__dict__)
        except NoUserWithEmailException:
            continue
        # delete org
        org_id = get_org(db, user.id)
        delete_user(db, user.id)
        if org_id:
            db.query(models.Organization).filter(
                models.Organization.id == str(org_id)
            ).delete()
            db.commit()


@contextmanager
def gen_users() -> Generator[Tuple[List[schemas.User], Any], None, None]:
    db = SessionLocal()
    try:
        # Cleanup in case the state is bad
        # If an organization has no references, delete it
        cleanup_test_users(db)

        # Setup
        for email in emails:
            make_user(db, email)
        users = [
            schemas.User(**get_user_by_email(db, email).__dict__) for email in emails
        ]
        admin_user_id = users[0].id
        # Create friendly org
        admin_org_member = create_organization_and_assign_to_user(
            db, schemas.OrganizationCreate(name="Test Organization"), admin_user_id
        )
        friendly_user_id: Any = users[1].id
        res = upsert_organization_for_user(
            db, friendly_user_id, admin_org_member.organization_id
        )
        assert admin_org_member.organization_id == get_org(
            db, friendly_user_id
        ), "Org ID not set correctly"
        assert (
            res.organization_id == admin_org_member.organization_id
        ), "Org ID not set correctly"
        # Create adversary org
        advesary_admin_user_id = users[2].id
        adversary_org_id = create_organization(
            db, schemas.OrganizationCreate(name="Adversary Organization")
        )
        res = upsert_organization_for_user(db, advesary_admin_user_id, adversary_org_id)
        yield (users, db)
    finally:
        for email in emails:
            delete_user_by_email(db, email)


def gen_cred_params(
    name="Test Postgres",
    host="localhost",
    port="5432",
    user="postgres",
    password="postgres",
):
    return schemas.DbCredentialCreate(
        db_driver="postgres",
        name=name,
        is_default=True,
        db_host=host,
        db_port=port,
        db_user=user,
        db_password=password,
        db_database="test",
        db_extras={"sslmode": "disable"},
    )


@contextmanager
def get_user():
    db = SessionLocal()
    cleanup_test_users(db)
    test_email = "testuser@mercator.tech"
    make_user(db, test_email)
    test_user = get_user_by_email(db, test_email)
    try:
        yield (test_user, db)
    finally:
        last_db_conn = get_mru_conn(db, test_user.id)
        if last_db_conn:
            delete_conn(db, conn_id=last_db_conn.id, user_id=test_user.id)
        delete_user(db, test_user.id)


@contextmanager
def gen_cred(db, credential_create: schemas.DbCredentialCreate, by_user_id: int):
    cred = create_conn(db, credential_create, by_user_id)
    try:
        yield cred
    finally:
        if not cred:
            return
        delete_conn(db, cred.id, by_user_id)
