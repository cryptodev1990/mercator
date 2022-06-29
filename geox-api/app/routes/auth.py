import datetime
from urllib.parse import quote_plus, urlencode

from fastapi import APIRouter, Depends, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBearer

from starlette.requests import Request
from authlib.integrations.starlette_client import OAuth, OAuthError


from .auth_decorators import VerifyToken

from fastapi.responses import RedirectResponse

from ..crud import create_user, get_user_by_email, update_user_by_email

from ..models import SessionLocal, User

router = APIRouter()
oauth = OAuth()
token_auth_scheme = HTTPBearer()




@router.get('/verify_jwt')
async def verify_jwt(response: Response, token = Depends(token_auth_scheme)):
    result = VerifyToken(token.credentials).verify()
    if result.get("status"):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return result
    return {"msg": "OK"}


@router.get('/auth')
async def auth(request: Request):
    redirect_url = request.query_params.get("redirect")
    try:
        token = await oauth.auth0.authorize_access_token(request)
    except OAuthError as error:
        return error.error
    userinfo = token.get('userinfo')
    if userinfo:
        user = dict(userinfo)
        with SessionLocal() as db_session:
            existing_user = get_user_by_email(db_session, user['email'])
            now = datetime.datetime.utcnow()
            user['last_login_at'] = now.strftime(
                '%Y-%m-%d %H:%M:%S.%f')
            if existing_user:
                existing_user.last_login_at = now
                update_user_by_email(db_session, existing_user)
            else:
                new_user = create_user(db_session, User(
                    email=user['email'],
                    given_name=user.get('given_name'),
                    family_name=user.get('family_name'),
                    nickname=user['nickname'],
                    name=user.get('name'),
                    picture=user.get('picture'),
                    locale=user.get('locale'),
                    updated_at=user['updated_at'],
                    email_verified=user['email_verified'],
                    iss=user['iss'],
                    last_login_at=now
                ))
            request.session['user'] = user
    return RedirectResponse(url=redirect_url)