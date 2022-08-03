from datetime import datetime

from app import schemas
from app.crud.db_credentials import (
    create_conn_record,
    decrypt,
    delete_db_conn,
    encrypt,
    get_all_connections,
    get_last_created_connection_for_user,
)
from app.crud.user import (
    create_user,
    delete_user,
    get_organization_for_user,
    get_user_by_email,
)
from app.db.session import SessionLocal
from app.schemas.user import UserCreate


def make_user(test_email):
    return UserCreate(
        email=test_email,
        given_name="Test",
        family_name="User",
        name="testuser",
        nickname="testuser",
        email_verified=True,
        iss="https://mercator.tech",
        sub_id="testuser",
        picture="https://mercator.tech/testuser.png",
        locale="en-US",
        updated_at=datetime.utcnow(),
    )


def _create_user_and_then(run_func):
    db = SessionLocal()
    test_email = "testuser@mercator.tech"
    new_user = make_user(test_email)
    create_user(db, new_user)
    test_user = get_user_by_email(db, test_email)
    try:
        run_func(db, test_user)
    except Exception as e:
        # TODO figure out the mix between pydantic and sqlalchemy
        raise e
    finally:
        db = SessionLocal()
        last_db_conn = get_last_created_connection_for_user(db, test_user.id)  # type: ignore
        if last_db_conn:
            delete_db_conn(db, conn_id=last_db_conn.id, user_id=test_user.id)  # type: ignore
        delete_user(db, test_user.id)  # type: ignore


def test_encrypt():
    encoded = encrypt("test")
    assert decrypt(encoded.encode()) == "test"
    assert not decrypt(encrypt("testother").encode()) == "test"


def test_create_conn_no_org():
    def test_func(db, user: schemas.User):

        assert get_organization_for_user(db, user.id) is None
        assert get_all_connections(db, user) == []

        new_cred = schemas.DbCredentialCreate(
            db_driver="postgres",
            name="Test Postgres",
            is_default=True,
            db_host="localhost",
            db_port="5432",
            db_user="test",
            db_password="test",
            db_database="test",
            db_extras={"sslmode": "disable"},
        )
        create_conn_record(db, new_cred, user.id)
        assert get_all_connections(db, user)[0].name == "Test Postgres"

    _create_user_and_then(test_func)
