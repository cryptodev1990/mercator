import json
import os
import pathlib

from fastapi.testclient import TestClient
from app.crud.shape import create_shape
from app.crud.user import create_user, get_user_by_email

from app.main import app
from app.lib.access_token import get_access_token
from app.models.db import SessionLocal, engine
from app.schemas import GeoShapeCreate, UserCreate
from app.lib import config


access_token = get_access_token()
headers = {"Authorization": f"Bearer {access_token}"}


client = TestClient(app)

here = pathlib.Path(__file__).parent.resolve()

geojson = json.loads(
    open(os.path.join(here, "../fixtures/bbox.geojson")).read())


def setup_shape():
    cleanup(config.machine_account_email)
    with SessionLocal() as db_session:
        obj = GeoShapeCreate(name="test shape", geojson=geojson)
        create_user(db_session, UserCreate(
            sub_id=config.machine_account_sub_id,
            email=config.machine_account_email,
            given_name="Test",
            family_name="User",
            nickname="",
            name="",
            picture="",
            locale="en-US",
            updated_at=None,
            email_verified=False,
            iss="",
        ))
        user = get_user_by_email(db_session, config.machine_account_email)
        shape = create_shape(db_session, obj, user_id=user.id)
        return user, shape


def cleanup(email):
    engine.execute(
        """
        BEGIN TRANSACTION;
          DELETE FROM shapes WHERE created_by_user_id IN (SELECT id FROM users WHERE email = %s);
          DELETE FROM users WHERE email = %s;
        END TRANSACTION;
        """, (email, email))


def test_auth_for_geofencer():
    response = client.get(
        "/geofencer/shapes/",
    )
    assert response.status_code == 403


def test_bounce_for_bad_bearer_token():
    response = client.get(
        "/geofencer/shapes/",
        headers={"Authorization": f"Bearer {access_token + '1'}"}
    )
    assert response.status_code == 403


def test_404_with_auth():
    try:
        response = client.get(
            "/geofencer/shapes/",
            headers=headers
        )
        assert response.status_code == 404
        with SessionLocal() as db_session:
            user = get_user_by_email(db_session, config.machine_account_email)
            assert user.id
            assert user.email == config.machine_account_email
    finally:
        cleanup(config.machine_account_email)


def test_create_shape():
    try:
        response = client.post(
            "/geofencer/shapes",
            json={"name": "test shape", "geojson": geojson},
            headers=headers
        )
        assert response.status_code == 200
        assert response.json().get("uuid")
        assert response.json().get("created_at")
        assert response.json().get("geojson")[
            "geometry"] == geojson["geometry"]
        assert response.json().get("geojson")["type"] == "Feature"
    finally:
        cleanup(config.machine_account_email)


def test_read_shape():
    _, shape = setup_shape()
    # Setup
    try:
        # Test body
        response = client.get(
            "/geofencer/shapes/" + str(shape.uuid),
            json={"name": "test shape", "geojson": geojson},
            headers=headers
        )
        assert response.json().get("uuid") == shape.uuid
        assert response.json().get(
            "created_at") == shape.created_at.strftime('%Y-%m-%dT%H:%M:%S.%f')
        assert response.json().get("geojson") == shape.geojson
    finally:
        cleanup(config.machine_account_email)


def test_read_no_shape():
    try:
        fake_uuid = '123e4567-e89b-12d3-a456-426614174000'
        response = client.get(
            "/geofencer/shapes/" + fake_uuid,
            json={"name": "test shape", "geojson": geojson},
            headers=headers
        )
        assert response.json().get("uuid") == None
        assert response.json().get("created_at") == None
        assert response.json().get("geojson") == None
    finally:
        cleanup(config.machine_account_email)


def test_update_shape():
    _, shape = setup_shape()
    edited_geojson = json.loads(
        open(os.path.join(here, "../fixtures/edited-bbox.geojson")).read())

    try:
        response = client.put(
            f"/geofencer/shapes/",
            json={"uuid": str(shape.uuid), "name": "edited test shape",
                  "geojson": edited_geojson},
            headers=headers
        )
        assert response.status_code == 200
        assert response.json().get("name") == "edited test shape", "Name should be updated"
        assert response.json().get("geojson")["geometry"] == edited_geojson["geometry"], "GeoJSON should be updated"
        assert response.json().get("geojson")["geometry"] != geojson["geometry"], "GeoJSON should be updated"
        assert shape.created_at.strftime('%Y-%m-%dT%H:%M:%S.%f') == response.json().get(
            "created_at"), "created_at should be the same"
        assert shape.updated_at.strftime('%Y-%m-%dT%H:%M:%S.%f') < response.json().get(
            "updated_at"), "updated_at should be updated"
    finally:
        cleanup(config.machine_account_email)


def test_soft_delete_update_shape():
    _, shape = setup_shape()
    edited_geojson = json.loads(
        open(os.path.join(here, "../fixtures/edited-bbox.geojson")).read())

    try:
        response = client.put(
            f"/geofencer/shapes/",
            json={"uuid": shape.uuid, "should_delete": True},
            headers=headers
        )
        assert response.status_code == 200
        assert response.json().get("name") == "edited test shape", "Name should be updated"
        assert response.json().get("geojson")["geometry"] == edited_geojson["geometry"], "GeoJSON should be updated"
        assert shape.created_at.strftime('%Y-%m-%dT%H:%M:%S.%f') == response.json().get(
            "created_at"), "created_at should be the same"
        assert shape.updated_at < response.json().get("updated_at"), "updated_at should be updated"
    finally:
        cleanup(config.machine_account_email)
