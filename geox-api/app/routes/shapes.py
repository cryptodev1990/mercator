import logging
from enum import Enum
from typing import List, Optional, Union

from fastapi import APIRouter, Depends
from pydantic import UUID4
from geojson_pydantic import Point, Polygon, LineString, Feature
from sqlalchemy import func, select, text

from app.crud import shape as crud
from app.dependencies import UserSession, get_app_user_session, verify_token
from app.schemas import (
    GeoShape,
    GeoShapeCreate,
    GeoShapeRead,
    GeoShapeUpdate,
    ShapeCountResponse,
)

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
        organization_id = db_session.execute(
            select(func.app_user_org())).scalar()
        shapes = crud.get_all_shapes_by_organization(
            db_session, organization_id)
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
    shapes = crud.get_shapes_related_to_geom(
        user_session.session, operation, geom)
    return shapes
