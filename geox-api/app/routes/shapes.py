import logging
from enum import Enum
from typing import List, Optional, Union, cast

from fastapi import APIRouter, Depends, HTTPException
from geojson_pydantic import Feature, LineString, Point, Polygon
from pydantic import UUID4
from sqlalchemy import func, select

from app.core.config import Settings, get_settings
from app.crud import shape as crud
from app.crud.organization import get_active_org, organization_s3_enabled
from app.dependencies import UserSession, get_app_user_session, verify_token
from app.schemas import (
    CeleryTaskResponse,
    GeoShape,
    GeoShapeCreate,
    GeoShapeUpdate,
    ShapeCountResponse,
)
from app.worker import copy_to_s3

logger = logging.getLogger(__name__)

router = APIRouter(tags=["geofencer"], dependencies=[Depends(verify_token)])


class GetAllShapesRequestType(str, Enum):
    """Valid shape request types."""

    user = "user"
    organization = "organization"


@router.post("/geofencer/shapes", response_model=GeoShape)
def create_shape(
    geoshape: GeoShapeCreate,
    user_session: UserSession = Depends(get_app_user_session),
) -> GeoShape:
    """Create a shape."""
    shape = crud.create_shape(user_session.session, geoshape)
    return shape


@router.get("/geofencer/shapes", response_model=List[GeoShape])
def get_all_shapes(
    rtype: GetAllShapesRequestType,
    user_session: UserSession = Depends(get_app_user_session),
) -> Optional[List[GeoShape]]:
    """Read shapes."""
    # Failure cases:
    # No shapes
    # Invalid user_id, organization_id
    # Unable to authorize for organization
    user = user_session.user
    db_session = user_session.session
    shapes = []
    if rtype == GetAllShapesRequestType.user:
        shapes = crud.get_all_shapes_by_user(db_session, user.id)
    elif rtype == GetAllShapesRequestType.organization:
        organization_id = db_session.execute(select(func.app_user_org())).scalar()
        shapes = crud.get_all_shapes_by_organization(
            db_session, organization_id=organization_id
        )
    return shapes


@router.get("/geofencer/shapes/{uuid}", response_model=GeoShape)
def get_shape(
    uuid: UUID4,
    user_session: UserSession = Depends(get_app_user_session),
    responses={404: {"details": "No shape with that ID found."}},
) -> Optional[GeoShape]:
    """Read a shape."""
    shape = crud.get_shape(user_session.session, uuid)
    if shape is None:
        raise HTTPException(404)
    return shape


@router.put("/geofencer/shapes/{uuid}", response_model=GeoShape)
def update_shape(
    geoshape: GeoShapeUpdate,
    user_session: UserSession = Depends(get_app_user_session),
) -> Optional[GeoShape]:
    """Update a shape."""
    shape: Optional[GeoShape]
    if geoshape.should_delete:
        logger.warning(
            "PUT /geofencer/shapes for deleting a shape is deprecated. Use DELETE /geofencer/shapes/{uuid}"
        )
        crud.delete_shape(user_session.session, geoshape.uuid)
        return None
    else:
        shape = crud.update_shape(user_session.session, geoshape)
        return shape


@router.post("/geofencer/shapes/bulk", response_model=ShapeCountResponse)
def bulk_create_shapes(
    geoshapes: List[GeoShapeCreate],
    user_session: UserSession = Depends(get_app_user_session),
) -> ShapeCountResponse:
    """Create multiple shapes."""
    shapes_uuid = crud.create_many_shapes(user_session.session, geoshapes)
    return ShapeCountResponse(num_shapes=len(shapes_uuid))


@router.delete("/geofencer/shapes/bulk", response_model=ShapeCountResponse)
def bulk_delete_shapes(
    shape_uuids: List[UUID4],
    user_session: UserSession = Depends(get_app_user_session),
) -> ShapeCountResponse:
    """Create multiple shapes."""
    row_count = crud.delete_many_shapes(user_session.session, shape_uuids)
    return ShapeCountResponse(num_shapes=row_count)


@router.get("/geofencer/shapes/op/count", response_model=ShapeCountResponse)
def get_shape_count(
    user_session: UserSession = Depends(get_app_user_session),
) -> ShapeCountResponse:
    """Get shape count."""
    shape_count = crud.get_shape_count(user_session.session)
    return ShapeCountResponse(num_shapes=shape_count)


@router.get("/geofencer/shapes/op/contains", response_model=List[Feature])
def get_shapes_containing_point(
    lat: float,
    lng: float,
    user_session: UserSession = Depends(get_app_user_session),
) -> List[Feature]:
    """Get shapes containing a point."""
    shapes = crud.get_shapes_containing_point(user_session.session, lat, lng)
    return shapes


@router.post("/geofencer/shapes/op/{operation}", response_model=List[Feature])
def get_shapes_by_operation(
    operation: crud.GeometryOperation,
    geom: Union[Point, Polygon, LineString],
    user_session: UserSession = Depends(get_app_user_session),
) -> List[Feature]:
    """Get shapes by operation."""
    shapes = crud.get_shapes_related_to_geom(user_session.session, operation, geom)
    return shapes


def run_shapes_export(user_session: UserSession, settings: Settings):
    org_id = get_active_org(user_session.session, user_session.user.id)
    if org_id is None:
        raise HTTPException(
            status_code=403, detail="No organization found."  # type: ignore
        )
    if not organization_s3_enabled(user_session.session, org_id):
        raise HTTPException(
            status_code=403, detail="Data export is not enabled for this account."  # type: ignore
        )
    # TODO: this should be a permission on shapes
    if settings.aws_s3_url is None:
        raise HTTPException(
            status_code=501, detail="Data export is not configured."  # type: ignore
        )
    aws_secret_access_key: Optional[str]
    if settings.aws_s3_upload_secret_access_key:
        aws_secret_access_key = (
            settings.aws_s3_upload_secret_access_key.get_secret_value()
        )
    else:
        aws_secret_access_key = None
    aws_access_key_id = settings.aws_s3_upload_access_key_id
    task = copy_to_s3.delay(
        str(org_id),
        cast(str, settings.sqlalchemy_database_uri),
        settings.aws_s3_url,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    return CeleryTaskResponse(task_id=task.id)


@router.post(
    "/shapes/export",
    response_model=CeleryTaskResponse,
    responses={
        403: {"description": "Data export not enabled for this account"},
        501: {"description": "Data export not supported on the server."},
    },
)
def shapes_export(
    user_session: UserSession = Depends(get_app_user_session),
    settings: Settings = Depends(get_settings),
):
    """Export shapes to S3.

    This is an async task. Use `/tasks/results/{task_id}` to retrieve the status and results.
    """
    return run_shapes_export(user_session, settings)
