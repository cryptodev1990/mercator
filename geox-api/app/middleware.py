import re

from fastapi import Request
from starlette.responses import JSONResponse
from .models import SessionLocal
from .crud.user import create_or_update_user_from_bearer_data

from starlette.middleware.base import BaseHTTPMiddleware


from typing import List

from app.core.verify_token import VerifyToken


def strip_bearer(s: str) -> str:
    return s.replace("Bearer ", "")


def sync_user_data(auth_jwt_payload: dict):
    with SessionLocal() as db_session:
        return create_or_update_user_from_bearer_data(db_session, auth_jwt_payload)


class ProtectedRoutesMiddleware(BaseHTTPMiddleware):
    """Require authentication for a list of routes
    Also creates user profiles from a valid JWT from Auth0
    """

    def __init__(
        self,
        app,
        protected_routes: List[str] = [],
    ):
        super().__init__(app)
        self.protected_routes = protected_routes

    async def dispatch(self, request: Request, call_next):
        if any([re.match(pr, request.url.path) for pr in self.protected_routes]):
            if not request.headers.get("Authorization"):
                return JSONResponse(
                    content={"msg": "Missing Authorization"}, status_code=403
                )
            token = strip_bearer(request.headers["Authorization"])
            result = VerifyToken(token).verify()
            if result.get("status") == "error":
                return JSONResponse(content=result, status_code=403)
            # TODO this is a database transaction per authenticated request
            # We could simplify this by checking if the current sub_id is in redis
            # and seeing if we've run this function in the last 30 minutes
            user_data = sync_user_data(result)
            request.state.user = user_data
        response = await call_next(request)
        return response
