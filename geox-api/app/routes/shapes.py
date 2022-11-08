import logging
from typing import List, Optional, Tuple, Union

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from geojson_pydantic import Feature, LineString, Point, Polygon
from pydantic import UUID4  # pylint: disable=no-name-in-module

from app.core.celery_app import celery_app
from app.core.config import Settings, get_settings
from app.core.datatypes import Latitude, Longitude
from app.crud import shape as crud
from app.crud.namespaces import get_default_namespace
from app.crud.shape import (
    ShapeDoesNotExist,
    create_many_shapes,
    create_shape,
    delete_many_shapes,
    delete_shape,
    get_shape,
    select_shapes,
    update_shape,
)
from app.dependencies import (
    UserConnection,
    get_app_user_connection,
    verify_subscription,
    verify_token,
)
from app.schemas import (
    CeleryTaskResponse,
    CeleryTaskResult,
    GeoShape,
    GeoShapeCreate,
    GeoShapeUpdate,
    RequestErrorModel,
    ShapeCountResponse,
    ShapesDeletedResponse,
    ViewportBounds,
)
from app.worker import copy_to_s3

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["geofencer"], dependencies=[Depends(verify_token), Depends(verify_subscription)]
)


_RESPONSES = {
    key: (status_code, {"description": description, "model": RequestErrorModel})
    for key, status_code, description in [
        ("SHAPE_DOES_NOT_EXIST", 404, "Shape does not exist"),
        ("SERVICE_MISSING_FROM_SERVER", 501, "Data export not supported on the server"),
    ]
}


def _responses(*args):
    return dict(_RESPONSES[key] for key in args)


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
        settings.aws_s3_url,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        app_env=settings.app_env
    )
    return CeleryTaskResponse(task_id=task.id)


@router.get(
    "/geofencer/shapes/export/{task_id}",
    response_model=CeleryTaskResult,
    tags=["tasks"],
)
def get_status(task_id: str):
    """Retrieve results of a task."""
    task_result = celery_app.AsyncResult(task_id)
    result = CeleryTaskResult(
        task_id=task_id, task_status=task_result.status, task_result=task_result.result
    )
    return result


@router.post(
    "/geofencer/shapes/export",
    response_model=CeleryTaskResponse,
    responses=_responses("SERVICE_MISSING_FROM_SERVER"),
)
def shapes_export(
    user_conn: UserConnection = Depends(get_app_user_connection),
    settings: Settings = Depends(get_settings),
) -> CeleryTaskResponse:
    """Export shapes to S3.

    This is an async task. Use `/tasks/results/{task_id}` to retrieve the status and results.
    """
    # Needs to go before /geofencer/shapes/{shape_id}
    return run_shapes_export(user_conn, settings)


@router.post("/geofencer/shapes/bulk", response_model=ShapeCountResponse)
def bulk_create_shapes(
    data: List[GeoShapeCreate],
    user_conn: UserConnection = Depends(get_app_user_connection),
    namespace: Optional[UUID4] = Query(default=None),
) -> ShapeCountResponse:
    """Create multiple shapes."""
    # Needs to go before /geofencer/shapes/{shape_id}
    shape_ids = list(
        create_many_shapes(
            user_conn.connection,
            data,
            user_id=user_conn.user.id,
            organization_id=user_conn.organization.id,
            namespace_id=namespace,
        )
    )
    return ShapeCountResponse(num_shapes=len(shape_ids))


@router.post("/geofencer/shapes", response_model=GeoShape)
def _post_shapes(
    data: GeoShapeCreate, user_conn: UserConnection = Depends(get_app_user_connection)
) -> GeoShape:
    """Create a shape."""
    namespace_id = (
        data.namespace
        or get_default_namespace(user_conn.connection, user_conn.organization.id).id
    )
    shape = create_shape(
        user_conn.connection,
        user_id=user_conn.user.id,
        organization_id=user_conn.organization.id,
        geojson=data.geojson,
        name=data.name,
        properties=data.properties,
        geom=data.geometry,
        namespace_id=namespace_id,
    )
    return shape


# Read


@router.get("/geofencer/shapes/op/count", response_model=ShapeCountResponse)
def get_shape_count(
    user_conn: UserConnection = Depends(get_app_user_connection),
) -> ShapeCountResponse:
    """Get shape count."""
    shape_count = crud.get_shape_count(user_conn.connection)
    return ShapeCountResponse(num_shapes=shape_count)


@router.get("/geofencer/shapes/op/contains", response_model=List[Feature])
def get_shapes_containing_point(
    lat: Latitude,
    lng: Longitude,
    user_conn: UserConnection = Depends(get_app_user_connection),
) -> List[Feature]:
    """Get shapes containing a point."""
    shapes = crud.get_shapes_containing_point(user_conn.connection, lat, lng)
    return shapes


@router.get("/geofencer/shapes/{shape_id}", response_model=GeoShape)
def _get_shapes__shape_id(
    shape_id: UUID4,  # = Path(title="ID of the shape to get."),
    user_conn: UserConnection = Depends(get_app_user_connection),
) -> GeoShape:
    """Read a shape."""
    try:
        shape = get_shape(user_conn.connection, shape_id)
    except ShapeDoesNotExist as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from None
    return shape


@router.get("/geofencer/shapes", response_model=List[GeoShape])
def _get_shapes(
    namespace: Optional[UUID4] = Query(
        default=None,
        title="Namespace of shapes",
        description="Only include shapes in the specified namespace given its UUID or name.",
    ),
    user: Optional[bool] = Query(
        default=None,
        title="Get shapes for the current user",
        description="If TRUE, then only return shapes of the requesting user.",
    ),
    user_conn: UserConnection = Depends(get_app_user_connection),
    offset: int = Query(default=0, title="Item offset", ge=0),
    limit: int = Query(default=300, title="Number of shapes to retrieve", ge=1),
    shape_ids: Optional[List[UUID4]] = Query(None, title="List of shape ids"),
    bbox: Optional[Tuple[Longitude, Latitude, Longitude, Latitude]] = Query(
        default=None, title="Bounding box (min x, min y, max x, max y)"
    ),
) -> List[GeoShape]:
    """Read shapes.

    Will return 200 even if no shapes match the query, including the case in which the
    namespace does not exist.

    All non-empty query parameters are combined with `AND`.

    """
    bbox_obj: Optional[ViewportBounds]
    if bbox:
        try:
            bbox_obj = ViewportBounds.from_list(bbox)
        except (ValueError, TypeError):
            raise HTTPException(422, "Invalid bbox") from None
    else:
        bbox_obj = None
    user_id = user_conn.user.id if user else None
    return list(
        select_shapes(
            user_conn.connection,
            user_id=user_id,
            namespace_id=namespace,
            offset=offset,
            limit=limit,
            ids=shape_ids,
            bbox=bbox_obj,
        )
    )


# Update

# TODO - deprecate this
# Fix it http://localhost:8080/geofencer/shapes/%7Buuid%7D
@router.put(
    "/geofencer/shapes/{uuid}",
    response_model=GeoShape,
    deprecated=True,
    responses=_responses("SHAPE_DOES_NOT_EXIST"),
)
def _update_shapes__shape_id(
    # shape_id: UUID4,
    data: GeoShapeUpdate,
    user_conn: UserConnection = Depends(get_app_user_connection),
) -> Optional[GeoShape]:
    """Update a shape."""
    shape: Optional[GeoShape]
    if data.uuid is None:
        raise HTTPException(422, detail="uuid must be provided.")
    shape_id: UUID4 = data.uuid
    try:
        shape = update_shape(
            user_conn.connection,
            shape_id,
            user_id=user_conn.user.id,
            geojson=data.geojson,
            geometry=data.geometry,
            properties=data.properties,
            name=data.name,
            namespace_id=data.namespace,
        )
    except ShapeDoesNotExist as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from None
    return shape


@router.patch(
    "/geofencer/shapes/{shape_id}",
    response_model=GeoShape,
    responses=_responses("SHAPE_DOES_NOT_EXIST"),
)
def _patch_shapes__shape_id(
    data: GeoShapeUpdate,
    shape_id: UUID4 = Path(title="ID of the shape to edit."),
    user_conn: UserConnection = Depends(get_app_user_connection),
) -> GeoShape:
    """Update a shape."""
    try:
        shape = update_shape(
            user_conn.connection,
            shape_id,
            user_id=user_conn.user.id,
            geojson=data.geojson,
            geometry=data.geometry,
            properties=data.properties,
            name=data.name,
            namespace_id=data.namespace,
        )
    except ShapeDoesNotExist as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from None
    return shape


# Delete


@router.delete("/geofencer/shapes/bulk", response_model=ShapeCountResponse)
def bulk_delete_shapes(
    shape_uuids: List[UUID4],
    user_conn: UserConnection = Depends(get_app_user_connection),
) -> ShapeCountResponse:
    """Create multiple shapes."""
    shapes = list(
        delete_many_shapes(
            user_conn.connection, user_id=user_conn.user.id, ids=shape_uuids
        )
    )
    return ShapeCountResponse(num_shapes=len(shapes))


@router.delete(
    "/geofencer/shapes/{shape_id}",
    status_code=204,
    responses=_responses("SHAPE_DOES_NOT_EXIST"),
)
def _delete_shapes__shape_id(
    shape_id: UUID4,
    user_conn: UserConnection = Depends(get_app_user_connection),
) -> None:
    """Delete a shape."""
    try:
        delete_shape(
            user_conn.connection,
            shape_id,
            user_id=user_conn.user.id,
        )
    except ShapeDoesNotExist as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from None


@router.delete("/geofencer/shapes", response_model=ShapesDeletedResponse)
def _delete_shapes(
    shape_ids: Optional[List[UUID4]] = Query(None),
    user_conn: UserConnection = Depends(get_app_user_connection),
) -> ShapesDeletedResponse:
    """Create multiple shapes."""
    shapes = list(
        delete_many_shapes(
            user_conn.connection,
            user_id=user_conn.user.id,
            ids=shape_ids,
            exclusive=False,
        )
    )
    return ShapesDeletedResponse(deleted_ids=shapes)


## Operations
@router.post(
    "/geofencer/shapes/op/{operation}",
    response_model=List[Feature],
    responses={
        403: {"description": "Operation not enabled for this account"},
        501: {"description": "Operation not supported on the server."},
    },
)
def get_shapes_by_operation(
    operation: crud.GeometryOperation,
    geom: Union[Point, Polygon, LineString],
    user_conn: UserConnection = Depends(get_app_user_connection),
) -> List[Feature]:
    """Get shapes by operation."""
    shapes = crud.get_shapes_related_to_geom(user_conn.connection, operation, geom)
    return shapes
