import datetime
import logging
from asyncio.log import logger
from contextlib import contextmanager
from typing import Any, Generator, List, Tuple
from uuid import UUID

from app import schemas
from app.core.config import get_settings
from app.crud.db_credentials import create_conn, delete_conn, get_mru_conn
from app.crud.organization import (
    add_user_to_organization,
    add_user_to_organization_by_invite,
    create_organization,
    create_organization_and_assign_to_user,
    get_active_org,
    get_all_orgs_for_user,
    get_personal_org_id,
    hard_delete_organization,
)
from app.crud.user import (
    NoUserWithEmailException,
    create_user,
    delete_user,
    delete_user_by_email,
    get_user_by_email,
)
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)

settings = get_settings()


emails = [
    "testuser@mercator.tech",
    "testuser-friendly@mercator.tech",
    "testuser-adversary@mercator.tech",
    "testuser-noorg@mercator.tech",
]


def make_user(db, test_email, sub_id=None):
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
        sub_id=username if sub_id is None else sub_id,
        picture="https://mercator.tech/testuser.png",
        locale="en-US",
        updated_at=datetime.datetime.utcnow(),
    )
    return create_user(db, new_user)


@contextmanager
def use_managerial_user():
    db = SessionLocal()
    user = None
    try:
        try:
            user = get_user_by_email(db, settings.machine_account_email)
        except NoUserWithEmailException:
            user = make_user(
                db,
                settings.machine_account_email,
                sub_id=settings.machine_account_sub_id,
            )
        else:
            # Delete and make a new user if they exist
            delete_user_by_email(db, settings.machine_account_email)
            user = make_user(
                db,
                settings.machine_account_email,
                sub_id=settings.machine_account_sub_id,
            )
        org_id = get_active_org(db, user.id)
        assert org_id
        assert get_personal_org_id(db, user.id) == org_id
        logger.info(get_all_orgs_for_user(db, user.id))
        assert len(get_all_orgs_for_user(db, user.id)) == 1
        yield schemas.UserWithMembership(
            **user.__dict__, organization_id=org_id, is_personal=True
        )
    finally:
        if user:
            delete_user(db, user.id)


def cleanup_test_users(db):
    for email in emails:
        try:

            user = get_user_by_email(db, email)
            user = schemas.User(**user.__dict__)
        except NoUserWithEmailException:
            continue
        # delete org
        delete_user(db, user.id)
        orgs = get_all_orgs_for_user(db, user.id)
        for org in orgs:
            hard_delete_organization(db, org.id)


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

        res = add_user_to_organization_by_invite(
            db, friendly_user_id, admin_org_member.id, admin_org_member.organization_id
        )
        assert admin_org_member.organization_id == get_active_org(
            db, friendly_user_id
        ), "Org ID not set correctly"
        assert (
            res.organization_id == admin_org_member.organization_id
        ), "Org ID not set correctly"
        # Create adversary org
        advesary_admin_user_id = users[2].id
        adversary_org = create_organization(
            db,
            schemas.OrganizationCreate(name="Adversary Organization"),
            advesary_admin_user_id,
        )

        res = add_user_to_organization(db, advesary_admin_user_id, adversary_org.id)
        yield (users, db)
    finally:
        for email in emails:
            delete_user_by_email(db, email)


def gen_cred_params(
    name="Test Postgres",
    host="localhost",
    port="5432",
    user="postgres",
    password="postgres",  # pragma: allowlist secret
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


def is_valid_uuid(uuid_to_test):
    try:
        uuid_obj = UUID(uuid_to_test, version=4)
    except ValueError:
        return False
    return True
