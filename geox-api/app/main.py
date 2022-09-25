"""Main module of the app."""
import logging

from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from app import routes
from app.core.config import get_settings
from app.tiler import add_tiler_routes

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__VERSION__ = "0.0.1"

settings = get_settings()

app = FastAPI(
    title="Mercator API",
    contact={
        "email": settings.machine_account_email,
    },
    version=settings.version,
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=settings.backend_cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
    ],
)

app.include_router(routes.osm.router)
app.include_router(routes.health.router)
app.include_router(routes.shapes.router)
app.include_router(routes.tasks.router)
app.include_router(routes.info.router)

add_tiler_routes(app)


@app.get("/")
async def home():
    return "Have no sphere - Mercator, Inc 2022"
