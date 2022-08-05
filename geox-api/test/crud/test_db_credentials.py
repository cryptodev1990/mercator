from app import schemas
from app.crud.db_credentials import (
    create_conn_record,
    decrypt,
    delete_db_conn,
    encrypt,
    get_all_connections,
    get_conn_with_secrets,
    get_last_created_connection_for_user,
    update_db_conn,
)
from app.crud.user import delete_user, get_user, get_user_by_email
from app.db.session import SessionLocal

from ..utils import make_user


def make_fake_db_credentials():
    return schemas.DbCredentialCreate(
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


def _create_user_and_then(run_func):
    db = SessionLocal()
    test_email = "testuser@mercator.tech"
    make_user(db, test_email)
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

        assert get_user(db, user_id=user.id).organization_id is None
        assert get_all_connections(db, user) == []

        new_cred = make_fake_db_credentials()
        create_conn_record(db, new_cred, user.id)
        conn = get_all_connections(db, user)[0]
        assert conn.name == "Test Postgres"
        conn_secrets = get_conn_with_secrets(
            db, schemas.DbCredentialRead(id=conn.id, user_id=user.id)
        )
        assert conn_secrets
        assert conn_secrets.db_password == "test"
        assert conn_secrets.db_extras == {"sslmode": "disable"}

    _create_user_and_then(test_func)


def test_update_conn():
    def test_func(db, user: schemas.User):

        new_cred = make_fake_db_credentials()
        create_conn_record(db, new_cred, user.id)
        conn = get_all_connections(db, user)[0]
        assert conn.name == "Test Postgres"
        conn_secrets = get_conn_with_secrets(
            db, schemas.DbCredentialRead(id=conn.id, user_id=user.id)
        )
        assert conn_secrets
        assert conn_secrets.db_password == "test"
        assert conn_secrets.db_extras == {"sslmode": "disable"}
        update_db_conn(
            db,
            schemas.DbCredentialUpdate(
                id=conn.id, name="Test Postgres Updated", user_id=user.id
            ),
        )
        conn = get_all_connections(db, user)[0]
        assert conn.name == "Test Postgres Updated"
        update_db_conn(
            db,
            schemas.DbCredentialUpdate(
                id=conn.id, db_password="NEWPASS", user_id=user.id
            ),
        )
        new_conn_secrets = get_conn_with_secrets(
            db, schemas.DbCredentialRead(id=conn.id, user_id=user.id)
        )
        assert new_conn_secrets
        assert conn_secrets.db_password != new_conn_secrets.db_password

    _create_user_and_then(test_func)
