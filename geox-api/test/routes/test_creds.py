import pathlib
from test.utils import gen_cred, gen_cred_params, gen_users, is_valid_uuid, use_managerial_user

from fastapi.testclient import TestClient

from app.core.access_token import get_access_token
from app.core.config import get_settings
from app.db.session import engine
from app.main import app

access_token = get_access_token()

settings = get_settings()

client = TestClient(app)


here = pathlib.Path(__file__).parent.resolve()


def create_conn_http():
    return client.post(
        "/db_config/connections",
        json={
            "name": "test",
            "db_host": "localhost",
            "db_port": "5432",
            "db_user": "test",
            "db_password": "test",
            "db_database": "test",
            "db_driver": "postgres",
            "name": "test connection",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )


def cleanup():
    email = settings.machine_account_email
    engine.execute(
        """
        BEGIN TRANSACTION;
          DELETE FROM db_credentials WHERE created_by_user_id IN (SELECT id FROM users WHERE email = %s);
          DELETE FROM users WHERE email = %s;
        END TRANSACTION;
        """,
        (email, email),
    )


def test_create_db_conn():
    with use_managerial_user() as user:
        response = create_conn_http()

        r = response.json()
        assert response.status_code == 200
        assert is_valid_uuid(r["id"])
        assert r["name"] == "test connection"
        assert r["organization_id"] == str(user.organization_id)


def test_get_db_conn():
    with use_managerial_user() as user:
        response = create_conn_http()
        response = client.get(
            "/db_config/connections/{}".format(response.json()["id"]),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        r = response.json()
        assert response.status_code == 200
        assert is_valid_uuid(r["id"])
        assert r["name"] == "test connection"
        assert r["organization_id"] == str(user.organization_id)


def test_get_db_conn_not_found():
    with use_managerial_user() as user:
        fake_uuid = "7c8df305-55af-4273-9f23-c260a6cdf610"
        response = client.get(
            "/db_config/connections/{}".format(fake_uuid),
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 404


def test_get_db_conn_unauthorized():
    """Attempt reading a credential that is not owned by the user results in a 404"""
    with gen_users() as (users, db):
        cred = gen_cred_params()
        with gen_cred(db, cred, users[0].id) as cred:
            with use_managerial_user() as user:
                response = client.get(
                    f"/db_config/connections/{cred.id}",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                assert response.status_code == 404


def test_read_multiple_conns():
    with use_managerial_user() as user:
        response = create_conn_http()
        conn_uuids = [response.json()["id"]]
        response = create_conn_http()
        conn_uuids.append(response.json()["id"])
        response = client.get(
            "/db_config/connections",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert all([any([x in str(row) for x in conn_uuids]) for row in response.json(
        )]), f"All UUIDs ({', '.join(conn_uuids)}) must be in the list, saw " + str(response.json())


def test_update_conn():
    with use_managerial_user() as user:
        response = create_conn_http()
        conn_id = response.json()["id"]
        response = client.patch(
            f"/db_config/connections/{conn_id}",
            json={"name": "new name", "id": conn_id},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200, response.text
        assert response.json()["name"] == "new name"


def test_delete_conn():
    with use_managerial_user() as user:
        response = create_conn_http()
        conn_id = response.json()["id"]
        response = client.delete(
            f"/db_config/connections/{conn_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200, response.text
        assert response.text == "true"