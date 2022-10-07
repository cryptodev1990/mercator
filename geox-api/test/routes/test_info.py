import os
from uuid import UUID

from fastapi.testclient import TestClient
from pytest_fastapi_deps import fastapi_dep

from app import schemas
from app.core.config import Settings, get_settings
from app.dependencies import UserOrganization, get_current_user
from app.main import app

client = TestClient(app)

version = "0.0.1"
git_commit = "da6c97c1411ba2e80e427fbf18502281c1b015f4"  # pragma: allowlist secret

# Following instructions here https://fastapi.tiangolo.com/advanced/settings/#settings-and-testing
# TODO: not sure if this messes up other tests


def get_settings_override():
    env_file = os.environ.get("ENV_FILE")
    return Settings(git_commit=git_commit, version=version, _env_file=env_file)  # type: ignore


def test_into(fastapi_dep):
    with fastapi_dep(app).override({get_settings: get_settings_override}):
        response = client.get("/info")
        data = response.json()
        assert data == {"version": version, "git_commit": git_commit}


def get_current_user_override():
    """Skip JWT authorization and return test user info."""
    return UserOrganization(
        user=schemas.User(id=42, email="foo@example.com", is_active=True, sub_id=1),
        organization=schemas.Organization(
            id=UUID("7fdc4df2-cc77-4be2-a48a-0640cdbc563f"),
            name="foo",
            created_by_user_id=1,
        ),
    )


def test_current_user(fastapi_dep):
    with fastapi_dep(app).override({get_current_user: get_current_user_override}):
        response = client.get("/current_user")
        data = response.json()
        assert data == {"user_id": 42}
