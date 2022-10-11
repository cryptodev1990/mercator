# TODO: uncomment after launching namespaces
import logging
from tokenize import Name
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import UUID4

from app.crud.namespaces import (
    DefaultNamespaceCannotBeRenamedError,
    NamespaceDoesNotExistError,
    NamespaceExistsError,
    create_namespace,
    delete_namespace,
    get_namespace_by_id,
    select_namespaces,
    update_namespace,
)
from app.crud.shape import select_shapes
from app.dependencies import UserConnection, get_app_user_connection, verify_token
from app.schemas import (
    Namespace,
    NamespaceCreate,
    NamespaceUpdate,
    RequestErrorModel,
)

# from app.crud.namespaces import *

logger = logging.getLogger(__name__)

router = APIRouter(tags=["namespaces"], dependencies=[Depends(verify_token)])


# _RESPONSES = {
#     key: (status_code, {"description": description, "model": RequestErrorModel})
#     for key, status_code, description in [
#         ("NAMESPACE_EXISTS", 404, "Namespace does not exist"),
#         ("NAMESPACE_DOES_NOT_EXIST", 409, "Namespace exists"),
#     ]
# }


# def _responses(*args):
#     return dict([_RESPONSES[key] for key in args])


# @router.post("/geofencer/namespaces", responses=_responses("NAMESPACE_EXISTS"))
# async def _post_namespaces(
#     namespace: NamespaceCreate,
#     user_conn: UserConnection = Depends(get_app_user_connection),
# ) -> Namespace:
#     """Create a namespace."""
#     try:
#         return create_namespace(
#             user_conn.connection,
#             name=namespace.name,
#             properties=namespace.properties,
#             user_id=user_conn.user.id,
#             organization_id=user_conn.organization.id,
#         )
#     except NamespaceExistsError as exc:
#         raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc))


# ## Read
# @router.get(
#     "/geofencer/namespaces/{namespace_id}",
#     responses=_responses("NAMESPACE_DOES_NOT_EXIST"),
# )
# async def _get_namespaces__namespace_id(
#     namespace_id: UUID4,
#     user_conn: UserConnection = Depends(get_app_user_connection),
# ) -> Namespace:
#     """Return a namespace."""
#     try:
#         namespace = get_namespace_by_id(user_conn.connection, namespace_id)
#     except NamespaceDoesNotExistError as exc:
#         raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))
#     return Namespace


# @router.get(
#     "/geofencer/namespaces",
# )
# async def _get_namespaces(
#     id: Optional[UUID4] = Query(default=None, title="ID of the namespace"),
#     name: Optional[str] = Query(default=None, title="Name of the namespace"),
#     user_conn: UserConnection = Depends(get_app_user_connection),
# ) -> List[Namespace]:
#     """Return namespaces available to the user."""
#     # TODO: this is an n+1 query. Change to a single query.
#     namespaces = list(select_namespaces(user_conn.connection, id_=id, name=name))
#     return namespaces


# ## Update
# @router.patch(
#     "/geofencer/namespaces/{namespace_id}",
#     responses=_responses("NAMESPACE_DOES_NOT_EXIST", "NAMESPACE_EXISTS"),
# )
# async def _patch_namespaces(
#     data: NamespaceUpdate,
#     namespace_id: UUID4 = Path(title="Namespace to edit"),
#     user_conn: UserConnection = Depends(get_app_user_connection),
# ) -> Namespace:
#     """Return namespaces available to the user."""
#     try:
#         namespace = update_namespace(
#             user_conn.connection,
#             namespace_id,
#             name=data.name,
#             properties=data.properties,
#         )
#     except NamespaceDoesNotExistError as exc:
#         raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))
#     except NamespaceExistsError as exc:
#         raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc))
#     except DefaultNamespaceCannotBeRenamedError as exc:
#         raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
#     return namespace


# ## Delete
# @router.delete(
#     "/geofencer/namespaces/{namespace_id}",
#     status_code=204,
#     responses=_responses("NAMESPACE_DOES_NOT_EXIST"),
# )
# async def _delete_namespaces(
#     namespace_id: UUID4,
#     user_conn: UserConnection = Depends(get_app_user_connection),
# ) -> None:
#     """Return namespaces available to the user.

#     - 204: Success with no content

#     """
#     try:
#         delete_namespace(user_conn.connection, namespace_id)
#     except NamespaceDoesNotExistError as exc:
#         raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))
#     return None


# # don't need a bulk delete - there aren't that many namespaces
