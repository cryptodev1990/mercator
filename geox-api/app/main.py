import json
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette_authlib.middleware import AuthlibMiddleware as SessionMiddleware
from starlette.responses import HTMLResponse

from .routes import (
    health,
    tasks,
    auth
)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # can alter with time
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

secret_key = os.environ['APP_SECRET_KEY']

app.add_middleware(SessionMiddleware, secret_key=secret_key)


app.include_router(health.router)
app.include_router(tasks.router)
app.include_router(auth.router)


@app.get('/')
async def homepage(request: Request):
    user = request.session.get('user')
    if user:
        data = json.dumps(user)
        html = (
            f'<pre>{data}</pre>'
            '<a href="/logout">logout</a>'
        )
        return HTMLResponse(html)
    return HTMLResponse('<a href="/login">login</a>')
