import logging
from asyncio.log import logger
from enum import Enum
from typing import List, Optional

from fastapi import APIRouter, Depends, Request, Security
from pydantic import UUID4
from sqlalchemy.orm import Session

from app.crud import shape as crud
from app.dependencies import UserSession, get_app_user_session, verify_token
from app.schemas import (
    GeoShape,
    GeoShapeCreate,
    GeoShapeRead,
    GeoShapeUpdate,
    ShapeCountResponse,
    User,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["geofencer"], dependencies=[Depends(verify_token)])


class GetAllShapesRequestType(str, Enum):
    user = "user"
    organization = "organization"


from sqlalchemy import text


@router.get("/geofencer/shapes/{uuid}", response_model=GeoShape)
def get_shape(
    uuid: UUID4,
    user_session: UserSession = Depends(get_app_user_session),
) -> Optional[GeoShape]:
    logger.info(
        "app.user_id",
        user_session.session.execute(text("SELECT app_user_id()")).scalar(),
    )
    res = user_session.session.execute(
        text("SELECT organization_id, user_id from organization_members")
    ).fetchall()
    for org_member in res:
        logger.info(org_member)
    logger.info(
        "app.user_org",
        user_session.session.execute(text("SELECT app_user_org()")).scalar(),
    )
    return crud.get_shape(user_session.session, GeoShapeRead(uuid=uuid))


from sqlalchemy import func, select


@router.get("/geofencer/shapes", response_model=List[GeoShape])
def get_all_shapes(
    rtype: GetAllShapesRequestType,
    user_session: UserSession = Depends(get_app_user_session),
) -> Optional[List[GeoShape]]:
    user = user_session.user
    db_session = user_session.session
    shapes = []
    if rtype == GetAllShapesRequestType.user:
        shapes = crud.get_all_shapes_by_user(db_session, User(**user.__dict__))
    elif rtype == GetAllShapesRequestType.organization:
        organization_id = db_session.execute(select(func.app_user_org())).scalar()
        shapes = crud.get_all_shapes_by_organization(db_session, organization_id)
    return shapes


@router.post("/geofencer/shapes", response_model=GeoShape)
def create_shape(
    geoshape: GeoShapeCreate,
    user_session: UserSession = Depends(get_app_user_session),
) -> GeoShape:
    shape = crud.create_shape(
        user_session.session, geoshape, user_id=user_session.user.id
    )
    return shape


@router.put("/geofencer/shapes/{uuid}", response_model=GeoShape)
def update_shape(
    geoshape: GeoShapeUpdate,
    user_session: UserSession = Depends(get_app_user_session),
) -> Optional[GeoShape]:
    shape = crud.update_shape(user_session.session, geoshape, user_session.user.id)
    return shape


@router.delete("/geofencer/shapes/bulk", response_model=ShapeCountResponse)
def bulk_soft_delete_shapes(
    shape_uuids: List[UUID4],
    user_session: UserSession = Depends(get_app_user_session),
) -> ShapeCountResponse:
    shape_count = crud.bulk_soft_delete_shapes(
        user_session.session, shape_uuids, user_session.user.id
    )
    return shape_count


@router.post("/geofencer/shapes/bulk", response_model=ShapeCountResponse)
def bulk_create_shapes(
    geoshapes: List[GeoShapeCreate],
    user_session: UserSession = Depends(get_app_user_session),
) -> ShapeCountResponse:
    num_shapes_created = crud.bulk_create_shapes(
        user_session.session, geoshapes, user_session.user.id
    )
    return num_shapes_created
