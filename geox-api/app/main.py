import os

from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from .middleware import ProtectedRoutesMiddleware

from .routes import (
    health,
    tasks,
)

secret_key = os.environ['APP_SECRET_KEY']

app = FastAPI(
    middleware=[
        Middleware(CORSMiddleware, allow_origins=[
                   "*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]),
        Middleware(ProtectedRoutesMiddleware,
                   protected_routes=['/protected_health']),

    ]
)


app.include_router(health.router)
app.include_router(tasks.router)


@app.get('/')
async def home():
    return "Have no sphere - Mercator, Inc 2022"
