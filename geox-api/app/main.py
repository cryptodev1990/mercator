"""Main module of the app."""
import logging

from datadog import initialize
from ddtrace import tracer
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from app import routes
from app.core.config import get_settings
from app.tiler import add_tiler_routes

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__VERSION__ = "0.0.1"

settings = get_settings()

initialize(
    statsd_host=settings.statsd_host,
    statsd_port=settings.statsd_port,
    statsd_constant_tags=settings.statsd_tags,
)

tracer.configure(hostname=settings.tracer_host, port=settings.tracer_port)

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
app.include_router(routes.shape_metadata.router)
app.include_router(routes.tasks.router)
app.include_router(routes.info.router)
app.include_router(routes.namespaces.router)

add_tiler_routes(app)


@app.on_event("startup")
async def startup():
    Instrumentator().instrument(app).expose(app)


@app.get("/")
async def home():
    return "Have no sphere - Mercator, Inc 2022"
