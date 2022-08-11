import pytest

import pathlib
from app.core.access_token import get_access_token
from fastapi.testclient import TestClient
from app.core.config import get_settings
from app.db.session import engine

from app.main import app
from test.utils import is_valid_uuid


access_token = get_access_token()

settings = get_settings()

client = TestClient(app)


here = pathlib.Path(__file__).parent.resolve()

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


@pytest.mark.skip()
def test_create_db_conn():
        response = client.post(
            "/db_config/connections",
            json={
                "name": "test",
                "host": "localhost",
                "port": "5432",
                "user": "test",
                "password": "test",
                "database": "test",
                "name": "test connection",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        r = response.json()
        assert response.status_code == 200
        assert is_valid_uuid(r["id"])
        assert r["name"] == "test"
        assert r["organization_id"]
