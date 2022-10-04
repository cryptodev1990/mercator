import logging
from enum import Enum
from typing import List, Optional, Union, cast

from app.core.config import Settings, get_settings
from app.crud import shape as crud
from app.crud.organization import get_active_org
from app.dependencies import (UserConnection, get_app_user_connection,
                              verify_token)
from app.schemas import (CeleryTaskResponse, GeoShape, GeoShapeCreate,
                         GeoShapeMetadata, GeoShapeUpdate, ShapeCountResponse,
                         ViewportBounds)
from app.worker import copy_to_s3
from fastapi import APIRouter, Depends, HTTPException
from geojson_pydantic import Feature, LineString, Point, Polygon
from pydantic import UUID4
from sqlalchemy import func, select

logger = logging.getLogger(__name__)

router = APIRouter(tags=["geofencer"], dependencies=[Depends(verify_token)])


class GetAllShapesRequestType(str, Enum):
    """Valid shape request types."""

    user = "user"
    organization = "organization"


@router.post("/geofencer/shapes", response_model=GeoShape)
def create_shape(
    geoshape: GeoShapeCreate,
    user_conn: UserConnection = Depends(get_app_user_connection),
) -> GeoShape:
    """Create a shape."""
    shape = crud.create_shape(user_conn.connection, geoshape)
    return shape


@router.get("/geofencer/shapes", response_model=List[GeoShape])
def get_all_shapes(
    rtype: GetAllShapesRequestType,
    offset: int = 0,
    limit: int = 300,
    user_conn: UserConnection = Depends(get_app_user_connection),
) -> Optional[List[GeoShape]]:
    """Read shapes."""
    # Failure cases:
    # No shapes
    # Invalid user_id, organization_id
    # Unable to authorize for organization
    user = user_conn.user
    conn = user_conn.connection
    shapes = []
    if rtype == GetAllShapesRequestType.user:
        shapes = crud.get_all_shapes_by_user(
            conn, user.id, offset=offset, limit=limit)
    elif rtype == GetAllShapesRequestType.organization:
        organization_id = conn.execute(select(func.app_user_org())).scalar()
        if organization_id is None:
            raise HTTPException(403, detail="User has no organization.")
        shapes = crud.get_all_shapes_by_organization(
            conn,
            organization_id=organization_id,
            limit=limit,
            offset=offset,
        )
    return shapes


@router.get("/geofencer/shapes/{uuid}", response_model=GeoShape)
def get_shape(
    uuid: UUID4,
    user_conn: UserConnection = Depends(get_app_user_connection),
    responses={404: {"details": "No shape with that ID found."}},
) -> Optional[GeoShape]:
    """Read a shape."""
    shape = crud.get_shape(user_conn.connection, uuid)
    if shape is None:
        raise HTTPException(404)
    return shape


@router.put("/geofencer/shapes/{uuid}", response_model=GeoShape)
def update_shape(
    geoshape: GeoShapeUpdate,
    user_conn: UserConnection = Depends(get_app_user_connection),
) -> Optional[GeoShape]:
    """Update a shape."""
    shape: Optional[GeoShape]
    if geoshape.should_delete:
        logger.warning(
            "PUT /geofencer/shapes for deleting a shape is deprecated. Use DELETE /geofencer/shapes/{uuid}"
        )
        crud.delete_shape(user_conn.connection, geoshape.uuid)
        return None
    else:
        shape = crud.update_shape(user_conn.connection, geoshape)
        return shape


@router.post("/geofencer/shapes/bulk", response_model=ShapeCountResponse)
def bulk_create_shapes(
    geoshapes: List[GeoShapeCreate],
    user_conn: UserConnection = Depends(get_app_user_connection),
) -> ShapeCountResponse:
    """Create multiple shapes."""
    shapes_uuid = crud.create_many_shapes(user_conn.connection, geoshapes)
    return ShapeCountResponse(num_shapes=len(shapes_uuid))


@router.delete("/geofencer/shapes/bulk", response_model=ShapeCountResponse)
def bulk_delete_shapes(
    shape_uuids: List[UUID4],
    user_conn: UserConnection = Depends(get_app_user_connection),
) -> ShapeCountResponse:
    """Create multiple shapes."""
    row_count = crud.delete_many_shapes(user_conn.connection, shape_uuids)
    return ShapeCountResponse(num_shapes=row_count)


@router.get("/geofencer/shapes/op/count", response_model=ShapeCountResponse)
def get_shape_count(
    user_conn: UserConnection = Depends(get_app_user_connection),
) -> ShapeCountResponse:
    """Get shape count."""
    shape_count = crud.get_shape_count(user_conn.connection)
    return ShapeCountResponse(num_shapes=shape_count)


@router.get("/geofencer/shapes/op/contains", response_model=List[Feature])
def get_shapes_containing_point(
    lat: float,
    lng: float,
    user_conn: UserConnection = Depends(get_app_user_connection),
) -> List[Feature]:
    """Get shapes containing a point."""
    shapes = crud.get_shapes_containing_point(user_conn.connection, lat, lng)
    return shapes


@router.post("/geofencer/shapes/op/{operation}", response_model=List[Feature],
             responses={
    403: {"description": "Operation not enabled for this account"},
    501: {"description": "Operation not supported on the server."},
})
def get_shapes_by_operation(
    operation: crud.GeometryOperation,
    geom: Union[Point, Polygon, LineString],
    user_conn: UserConnection = Depends(get_app_user_connection),
) -> List[Feature]:
    """Get shapes by operation."""
    shapes = crud.get_shapes_related_to_geom(
        user_conn.connection, operation, geom)
    return shapes


def run_shapes_export(user_conn: UserConnection, settings: Settings):
    org = user_conn.organization
    if not org.s3_export_enabled:
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
        org.id,
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
    user_conn: UserConnection = Depends(get_app_user_connection),
    settings: Settings = Depends(get_settings),
):
    """Export shapes to S3.

    This is an async task. Use `/tasks/results/{task_id}` to retrieve the status and results.
    """
    return run_shapes_export(user_conn, settings)


@router.get("/geofencer/shape-metadata/bbox", response_model=List[GeoShapeMetadata], tags=["shape-metadata"])
def get_shape_metadata_by_bounding_box(
    min_x: float,
    min_y: float,
    max_x: float,
    max_y: float,
    user_conn: UserConnection = Depends(get_app_user_connection),
    limit: int = crud.DEFAULT_LIMIT,
    offset: int = 0,
) -> List[GeoShapeMetadata]:
    """Get shape metadata by bounding box."""
    bbox = ViewportBounds(min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y)
    shapes = crud.get_shape_metadata_by_bounding_box(
        user_conn.connection, bbox, limit, offset)
    return shapes


@ router.get("/geofencer/shape-metadata/search", response_model=List[GeoShapeMetadata], tags=["shape-metadata"])
def get_shape_metadata_matching_search(
    query: str,
    user_conn: UserConnection = Depends(get_app_user_connection),
    limit: int = crud.DEFAULT_LIMIT,
    offset: int = 0,
) -> List[GeoShapeMetadata]:
    """Get shape metadata by bounding box."""
    shapes = crud.get_shape_metadata_matching_search(
        user_conn.connection, query, limit, offset)
    return shapes


@router.get("/geofencer/shape-metadata", response_model=List[GeoShapeMetadata], tags=["shape-metadata"])
def get_all_shape_metadata(
    user_conn: UserConnection = Depends(get_app_user_connection),
    limit: int = crud.DEFAULT_LIMIT,
    offset: int = 0,
) -> List[GeoShapeMetadata]:
    """Get all shape metadata with pagination"""
    org_id = get_active_org(user_conn.connection, user_conn.user.id)
    if org_id is None:
        raise HTTPException(
            status_code=403, detail="No organization found."
        )
    shapes = crud.get_all_shape_metadata_by_organization(
        user_conn.connection, organization_id=org_id, limit=limit, offset=offset)
    return shapes
