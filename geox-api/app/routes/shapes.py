import logging
from enum import Enum
from typing import List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException
from geojson_pydantic import Feature, LineString, Point, Polygon
from pydantic import UUID4
from sqlalchemy import func, select, text

from app.core.config import Settings, get_settings
from app.crud import shape as crud
from app.crud.organization import get_active_org, organization_s3_enabled
from app.dependencies import UserSession, get_app_user_session, verify_token
from app.schemas import (
    CeleryTaskResponse,
    GeoShape,
    GeoShapeCreate,
    GeoShapeRead,
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
        shapes = crud.get_all_shapes_by_organization(db_session, organization_id)
    return shapes


@router.get("/geofencer/shapes/{uuid}", response_model=GeoShape)
def get_shape(
    uuid: UUID4,
    user_session: UserSession = Depends(get_app_user_session),
) -> Optional[GeoShape]:
    """Read a shape."""
    return crud.get_shape(user_session.session, GeoShapeRead(uuid=uuid))


@router.put("/geofencer/shapes/{uuid}", response_model=GeoShape)
def update_shape(
    geoshape: GeoShapeUpdate,
    user_session: UserSession = Depends(get_app_user_session),
) -> Optional[GeoShape]:
    """Update a shape."""
    shape: Optional[GeoShape]
    if geoshape.should_delete:
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


def _shapes_export(user_session: UserSession, settings: Settings):

    org_id = get_active_org(user_session.session, user_session.user.id)
    # TODO: this should be a permission on shapes
    if settings.aws_s3_uri is None:
        raise HTTPException(
            status_code=501, detail="Data export is not configured."  # type: ignore
        )
    if not organization_s3_enabled(user_session.session, str(org_id)):
        raise HTTPException(
            status_code=403, detail="Data export is not enabled for this account."  # type: ignore
        )
    task = copy_to_s3.delay(org_id)
    return CeleryTaskResponse(task_id=task.id)


@router.post(
    "/shapes/export",
    response_model=CeleryTaskResponse,
    responses={
        403: {"description": "Data export not enabled for this account."},
        501: {"description": "Shape export is not configured on the server."},
    },
)
def shapes_export(
    user_session: UserSession = Depends(get_app_user_session),
    settings: Settings = Depends(get_settings),
):
    """Export shapes to S3.

    This is an async task. Use `/tasks/results/{task_id}` to retieve the status and results.
    """
    return _shapes_export(user_session, settings)
