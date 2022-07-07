from typing import Optional, List

from fastapi import APIRouter, Request
from pydantic import UUID4

from app.schemas import GeoShape, GeoShapeRead, GeoShapeUpdate, User, GeoShapeCreate

from ..models import SessionLocal
from ..crud import shape as crud


router = APIRouter(tags=["geofencer"])


@router.get("/geofencer/shapes/{uuid}")
def get_shape(uuid: UUID4) -> Optional[GeoShape]:
    with SessionLocal() as db_session:
        return crud.get_shape(db_session, GeoShapeRead(uuid=uuid))


@router.get("/geofencer/shapes")
def get_all_shapes(type: str, request: Request) -> Optional[List[GeoShape]]:
    # Set by ProtectedRoutesMiddleware
    user = request.state.user
    with SessionLocal() as db_session:
        if type == "user":
            return crud.get_all_shapes_by_user(db_session, User(**user))
        elif type == "email_domain":
            email_domain = user.email.split("@")[1]
            return crud.get_all_shapes_by_email_domain(db_session, email_domain)


@router.post("/geofencer/shapes")
def create_shape(request: Request, geoshape: GeoShapeCreate) -> Optional[List[GeoShape]]:
    # Set by ProtectedRoutesMiddleware
    user = request.state.user
    with SessionLocal() as db_session:
        return crud.create_shape(db_session, geoshape, user_id=user.id)


@router.put("/geofencer/shapes/")
def update_shape(request: Request, geoshape: GeoShapeUpdate) -> Optional[List[GeoShape]]:
    # Set by ProtectedRoutesMiddleware
    user = request.state.user
    if geoshape.should_delete:
        geoshape.deleted_by_user_id = user.id
    with SessionLocal() as db_session:
        return crud.update_shape(db_session, geoshape)
