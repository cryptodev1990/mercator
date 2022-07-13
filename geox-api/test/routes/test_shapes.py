from typing import Callable
import json
import os
import pathlib

from fastapi import status
from fastapi.testclient import TestClient

from app.crud.shape import create_shape
from app.crud.user import create_user, get_user_by_email
from app.lib import config
from app.lib.access_token import get_access_token
from app.main import app
from app.models.db import SessionLocal, engine
from app.models import Shape
from app.schemas import GeoShapeCreate, UserCreate


def ymd(x):
    return x.strftime('%Y-%m-%dT%H:%M:%S.%f')


def assert_ok(response):
    assert response.status_code == status.HTTP_200_OK, "Status should be ok"


access_token = get_access_token()
headers = {"Authorization": f"Bearer {access_token}"}


client = TestClient(app)

here = pathlib.Path(__file__).parent.resolve()

geojson = json.loads(
    open(os.path.join(here, "../fixtures/bbox.geojson")).read())


def setup_shape():
    cleanup()
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


def cleanup():
    email = config.machine_account_email
    engine.execute(
        """
        BEGIN TRANSACTION;
          DELETE FROM shapes WHERE created_by_user_id IN (SELECT id FROM users WHERE email = %s);
          DELETE FROM users WHERE email = %s;
        END TRANSACTION;
        """, (email, email))


def run_shape_test(test_func: Callable[[Shape], None]):
    _, shape = setup_shape()
    try:
        test_func(shape)
    finally:
        cleanup()


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
            "/geofencer/shapesa/",
            headers=headers
        )
        assert response.status_code == 404
        with SessionLocal() as db_session:
            user = get_user_by_email(db_session, config.machine_account_email)
            assert user.id
            assert user.email == config.machine_account_email
    finally:
        cleanup()


def test_create_shape():
    try:
        response = client.post(
            "/geofencer/shapes",
            json={"name": "test shape", "geojson": geojson},
            headers=headers
        )
        assert_ok(response)
        body = response.json()

        assert body.get("uuid")
        assert body.get("created_at")
        assert body.get("geojson")[
            "geometry"] == geojson["geometry"]
        assert body.get("geojson")["type"] == "Feature"
    finally:
        cleanup()


def test_read_shape():
    def _test(shape: Shape):
        response = client.get(
            "/geofencer/shapes/" + str(shape.uuid),
            json={"name": "test shape", "geojson": geojson},
            headers=headers
        )
        body = response.json()
        assert body.get("uuid") == str(shape.uuid)
        assert body.get("created_at") == ymd(shape.created_at)
        assert json.dumps(body.get("geojson")) == shape.geojson.json()
    run_shape_test(_test)


def test_read_no_shape():
    try:
        fake_uuid = '123e4567-e89b-12d3-a456-426614174000'
        response = client.get(
            "/geofencer/shapes/" + fake_uuid,
            json={"name": "test shape", "geojson": geojson},
            headers=headers
        )
        body = response.json()
        assert body.get("uuid") == None
        assert body.get("created_at") == None
        assert body.get("geojson") == None
    finally:
        cleanup()


def test_update_shape():
    def _test(shape: Shape):
        edited_geojson = json.loads(
            open(os.path.join(here, "../fixtures/edited-bbox.geojson")).read())
        response = client.put(
            f"/geofencer/shapes/" + str(shape.uuid),
            json={"uuid": str(shape.uuid), "name": "edited test shape",
                  "geojson": edited_geojson},
            headers=headers
        )

        body = response.json()
        geom = body.get("geojson")["geometry"]
        assert_ok(response)
        assert body.get(
            "name") == "edited test shape", "Name should be updated"
        assert geom == edited_geojson["geometry"], "GeoJSON should be updated"
        assert geom != geojson["geometry"], "GeoJSON should be updated"
        assert ymd(shape.created_at) == body.get(
            "created_at"), "created_at should be the same"
        assert ymd(shape.updated_at) < body.get(
            "updated_at"), "updated_at should be updated"
    run_shape_test(_test)


def test_soft_delete_update_shape():
    def _test(shape: Shape):
        response = client.put(
            f"/geofencer/shapes/" + str(shape.uuid),
            json={"should_delete": True, "uuid": str(shape.uuid)},
            headers=headers
        )
        assert_ok(response)
        body = response.json()
        assert not body
    run_shape_test(_test)


def test_get_all_shapes_email_domain():
    def _test(shape: Shape):
        response = client.get(
            f"/geofencer/shapes?rtype=domain",
            headers=headers
        )
        assert_ok(response)
        body = response.json()
        # TODO the test user has the same email domain as the machine account
        # so any dev work I do contributes results to this test.
        assert len(body) >= 1
        assert any([r.get("uuid") == str(shape.uuid) for r in body])
    run_shape_test(_test)


def test_get_all_shapes_user():
    def _test(shape: Shape):
        response = client.get(
            f"/geofencer/shapes?rtype=user",
            headers=headers
        )
        assert_ok(response)
        body = response.json()
        assert len(body) == 1
        assert body[0].get("uuid") == str(shape.uuid)
    run_shape_test(_test)
