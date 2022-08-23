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


def test_delete_org():
    with use_managerial_user() as user:
        try:
            response = client.delete(
                "/organizations/{}".format(user.organization_id),
                headers={"Authorization": f"Bearer {access_token}"},
            )
        except Exception as e:
            assert "personal org" in str(e)


def test_update_org_no_org():
    with use_managerial_user() as user:
        try:
            response = client.put(
                "/organizations/{}".format(user.organization_id),
                json={
                    "name": "test",
                },
                headers={"Authorization": f"Bearer {access_token}"},
            )
        except Exception as e:
            assert "not found" in str(e)


def test_update_org():
    with use_managerial_user() as user:
        response = client.post(
            "/organizations",
            json={
                "name": "test",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        org_id = response.json()["organization_id"]

        response = client.put(
            "/organizations/{}".format(org_id),
            json={
                "name": "test 2",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        print(response.json())

        assert response.status_code == 200
        assert response.json()["name"] == "test 2"
