# pylint: disable=redefined-outer-name
import os
from uuid import UUID

from fastapi.testclient import TestClient
from pytest_fastapi_deps import fastapi_dep  # pylint: disable=unused-import

from app import schemas
from app.core.config import Settings, get_settings
from app.dependencies import UserOrganization, get_current_user_org
from app.main import app

from .conftest import ExampleDbAbc

client = TestClient(app)

version = "0.0.1"
git_commit = "da6c97c1411ba2e80e427fbf18502281c1b015f4"  # pragma: allowlist secret


def get_settings_override() -> Settings:
    env_file = os.environ.get("ENV_FILE")
    return Settings(git_commit=git_commit, version=version, _env_file=env_file)  # type: ignore


def test_into(fastapi_dep, db: ExampleDbAbc) -> None:
    # more overrides
    with fastapi_dep(app).override({get_settings: get_settings_override}):
        response = client.get("/info")
    data = response.json()
    assert response.status_code == 200
    assert data == {"version": version, "git_commit": git_commit}


def test_current_user(db: ExampleDbAbc) -> None:
    response = client.get("/current_user")
    data = response.json()
    assert response.status_code == 200
    assert data == {"user_id": db.alice.id}
