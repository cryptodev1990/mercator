"""Main module of the app."""

import logging

from datadog import initialize
from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from app import routes
from app.core.config import get_settings
from app.core.stats import attach_stats_middleware, stats
from app.tiler import add_tiler_routes

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__VERSION__ = "0.0.1"

settings = get_settings()

initialize(**settings.dd_init_kwargs)

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

for route in [
    routes.osm.router,
    routes.billing.router,
    routes.health.router,
    routes.shapes.router,
    routes.shape_metadata.router,
    routes.tasks.router,
    routes.info.router,
    routes.namespaces.router,
]:
    app.include_router(route)

add_tiler_routes(app)
attach_stats_middleware(app)


@app.on_event("startup")
async def startup():
    stats.start()


@app.get("/")
async def home():
    return "Have no sphere - Mercator, Inc 2022"
