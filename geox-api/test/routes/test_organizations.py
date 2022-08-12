import pathlib
from datetime import datetime
from test.utils import is_valid_uuid, use_managerial_user

from fastapi.testclient import TestClient

from app.core.access_token import get_access_token
from app.core.config import get_settings
from app.main import app

access_token = get_access_token()

settings = get_settings()

client = TestClient(app)


here = pathlib.Path(__file__).parent.resolve()


def test_get_organization():
    with use_managerial_user() as user:
        response = client.get(
            "/organizations",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        r = response.json()
        assert is_valid_uuid(r[0]["id"])
        assert r[0]["name"] == "duber+ManagementApi Workspace"
        assert r[0]["is_personal"] == True


def test_create_org():
    with use_managerial_user() as user:
        then = datetime.utcnow().isoformat()
        response = client.post(
            "/organizations",
            json={
                "name": "test",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        r = response.json()
        assert is_valid_uuid(r["organization_id"])
        assert r["id"] == user.id
        assert str(r["organization_id"]) != str(user.organization_id)
