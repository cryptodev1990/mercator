import datetime
import os

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder

from starlette.requests import Request
from authlib.integrations.starlette_client import OAuth, OAuthError

from fastapi.responses import RedirectResponse

from ..crud import create_user, get_user_by_email, update_user_by_email

from ..models import SessionLocal, User

router = APIRouter()


oauth = OAuth()


oauth.register(
    "auth0",
    client_id=os.environ["AUTH0_CLIENT_ID"],
    client_secret=os.environ["AUTH0_CLIENT_SECRET"],
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{os.environ["AUTH0_DOMAIN"]}/.well-known/openid-configuration'
)


@router.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.auth0.authorize_redirect(request, redirect_uri)


@router.get('/auth')
async def auth(request: Request):
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
    return RedirectResponse(url='/')


@router.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    print(request.session)
    return RedirectResponse(url='/')
