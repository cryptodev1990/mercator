from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app

client = TestClient(app)

version = "0.0.1"
git_commit = "da6c97c1411ba2e80e427fbf18502281c1b015f4"

# Following instructions here https://fastapi.tiangolo.com/advanced/settings/#settings-and-testing
# TODO: not sure if this messes up other tests


def get_settings_override():
    return Settings(git_commit=git_commit, version=version)


app.dependency_overrides[get_settings] = get_settings_override


def test_into():
    response = client.get("/info")
    data = response.json()
    assert data == {"version": version, "git_commit": git_commit}
