import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import UUID4  # pylint: disable=no-name-in-module
from typing import Any, Dict, Generator, List, Optional, cast

from app.core.logging import get_logger
from app.crud.namespaces import (
    DefaultNamespaceCannotBeRenamedError,
    NamespaceDoesNotExistError,
    NamespaceExistsError,
    create_namespace,
    delete_namespace,
    get_default_namespace,
    get_namespace,
    select_namespaces,
    update_namespace,
)
from app.crud.shape import select_shape_metadata
from app.dependencies import (
    UserConnection,
    get_app_user_connection,
    verify_subscription,
    verify_token,
)
from app.schemas import Namespace, NamespaceCreate, NamespaceUpdate, RequestErrorModel
from app.schemas.namespaces_api import NamespaceResponse
from sqlalchemy import delete
from app.db.metadata import shapes as shapes_tbl

# from app.crud.namespaces import *

logger = get_logger(__name__)

router = APIRouter(
    tags=["namespaces"],
    dependencies=[Depends(verify_token), Depends(verify_subscription)],
)


_RESPONSES = {
    key: (status_code, {"description": description, "model": RequestErrorModel})
    for key, status_code, description in [
        ("NAMESPACE_EXISTS", 404, "Namespace does not exist"),
        ("NAMESPACE_DOES_NOT_EXIST", 409, "Namespace exists"),
    ]
}

# pylint: disable=consider-using-dict-comprehension
def _responses(*args):
    return dict([_RESPONSES[key] for key in args])


# pylint: enable=consider-using-dict-comprehension


@router.post(
    "/geofencer/namespaces",
    responses=_responses("NAMESPACE_EXISTS"),
    response_model=Namespace,
)
async def _post_namespaces(
    namespace: NamespaceCreate,
    user_conn: UserConnection = Depends(get_app_user_connection),
) -> Namespace:
    """Create a new namespace."""
    try:
        return create_namespace(
            user_conn.connection,
            name=namespace.name,
            properties=namespace.properties,
            user_id=user_conn.user.id,
            organization_id=user_conn.organization.id,
        )
    except NamespaceExistsError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from None


# Read
@router.get(
    "/geofencer/namespaces/{namespace_id}",
    responses=_responses("NAMESPACE_DOES_NOT_EXIST"),
    response_model=NamespaceResponse,
)
async def _get_namespaces__namespace_id(
    namespace_id: UUID4,
    user_conn: UserConnection = Depends(get_app_user_connection),
) -> NamespaceResponse:
    """Return a namespace."""
    conn = user_conn.connection
    try:
        namespace = NamespaceResponse.from_orm(get_namespace(conn, namespace_id))
    except NamespaceDoesNotExistError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from None
    namespace.shapes = list(select_shape_metadata(conn, namespace_id=namespace.id))
    return namespace


@router.get("/geofencer/namespaces", response_model=List[NamespaceResponse])
async def _get_namespaces(
    # pylint: disable=redefined-builtin
    id: Optional[UUID4] = Query(default=None, title="ID of the namespace"),
    # pylint: enable=redefined-builtin
    name: Optional[str] = Query(default=None, title="Name of the namespace"),
    includeShapes: bool = Query(default=True),
    user_conn: UserConnection = Depends(get_app_user_connection),
) -> List[NamespaceResponse]:
    """Return namespaces available to the user."""
    conn = user_conn.connection
    namespaces = [
        NamespaceResponse.from_orm(nm)
        for nm in select_namespaces(conn, id_=id, name=name)
    ]
    # TODO: this is an n+1 query. Change to a single query. However, the number of
    # namespaces is generally small so this may not be that bad
    if includeShapes:
        for nm in namespaces:
            nm.shapes = list(select_shape_metadata(conn, namespace_id=nm.id))
    return namespaces


@router.patch(
    "/geofencer/namespaces/{namespace_id}/relationships/shapes",
    response_model=NamespaceResponse,
)
async def _patch_namespaces_shapes(
    reqBody: Dict[str, Any],
    namespace_id: UUID4 = Path(title="Namespace to edit"),
    user_conn: UserConnection = Depends(get_app_user_connection),
) -> Namespace:
    if "data" in reqBody and not reqBody['data']:
        deleteStmt = delete(shapes_tbl).where(shapes_tbl.c.namespace_id == namespace_id)
        try:
            user_conn.connection.execute(deleteStmt)
            namespace = NamespaceResponse.from_orm(get_namespace(user_conn.connection, namespace_id))
            return namespace
        except Exception:
            raise HTTPException(status_code=500)
    else:
        raise HTTPException(status_code=400)


# Update
@router.patch(
    "/geofencer/namespaces/{namespace_id}",
    responses=_responses("NAMESPACE_DOES_NOT_EXIST", "NAMESPACE_EXISTS"),
    response_model=NamespaceResponse,
)
async def _patch_namespaces(
    data: NamespaceUpdate,
    namespace_id: UUID4 = Path(title="Namespace to edit"),
    user_conn: UserConnection = Depends(get_app_user_connection),
) -> Namespace:
    """Return namespaces available to the user."""
    try:
        namespace = update_namespace(
            user_conn.connection,
            namespace_id,
            data,
        )
    except NamespaceDoesNotExistError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from None
    except NamespaceExistsError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from None
    except DefaultNamespaceCannotBeRenamedError as exc:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from None
    return namespace


# Delete
@router.delete(
    "/geofencer/namespaces/{namespace_id}",
    status_code=204,
    responses=_responses("NAMESPACE_DOES_NOT_EXIST"),
)
async def _delete_namespaces(
    namespace_id: UUID4,
    user_conn: UserConnection = Depends(get_app_user_connection),
) -> None:
    """Return namespaces available to the user.

    - 204: Success with no content

    """
    conn = user_conn.connection
    default_namespace_id = get_default_namespace(conn, user_conn.organization.id).id
    # The crud function should allow deleting any namespace so implement the inability
    # to delete the default namespace here.
    if namespace_id == default_namespace_id:
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="Unable to delete the default namespace."
        ) from None
    try:
        delete_namespace(user_conn.connection, namespace_id)
    except NamespaceDoesNotExistError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from None
    return None


# don't need a bulk delete - there aren't that many namespaces
