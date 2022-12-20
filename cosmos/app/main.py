"""Fastapi main"""
import logging
import re

from fastapi import Depends, FastAPI, HTTPException
from fastapi.routing import APIRoute
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection  # type: ignore
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db import engine
from app.dependencies import get_conn
from app.routes.autocomplete import router as autocomplete_router
from app.routes.osm import router as osm_router
from app.schemas import HealthResponse, HealthStatus

logger = logging.getLogger(__name__)

__VERSION__ = "0.0.1"

settings = get_settings()

app = FastAPI(
    title="Mercator OSM API",
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

app.include_router(osm_router, prefix="/osm", tags=["osm"])
app.include_router(autocomplete_router, prefix="/autocomplete", tags=["autocomplete"])


async def db_health_check(conn: AsyncConnection) -> None:
    """Check if the database is up and running."""
    try:
        await conn.execute(text("SELECT 1"))
    except Exception as exc:
        raise DatabaseHealthError from exc


@app.on_event("startup")
async def _startup() -> None:
    # Log the version of the app
    logger.info("APP ENVIRONMENT=%s; VERSION=%s", settings.env, str(settings.version))
    async with engine.connect() as conn:
        await db_health_check(conn)


@app.on_event("shutdown")
async def _shutodwn() -> None:
    logger.info("Shutting down")
    await engine.dispose()


@app.get("/")
async def home() -> str:
    """Home page."""
    return "OSM seach API - © Mercator"


class DatabaseHealthError(Exception):
    """Exception raised when database is not healthy."""


@app.get("/health", tags=["health"])
async def health() -> HealthResponse:
    """API health check."""
    return HealthResponse(message=HealthStatus.OK)


@app.get("/health/db", tags=["health"])
async def db_health(conn: AsyncConnection = Depends(get_conn)) -> HealthResponse:
    """App database health check."""
    try:
        (await conn.execute(text("SELECT 1"))).scalar()
        return HealthResponse(message=HealthStatus.OK)
    except Exception:
        raise HTTPException(status_code=500, detail=HealthStatus.ERROR) from None


def _generate_operation_id(route: APIRoute) -> str:
    # operation_id = route.name + route.path_format
    operation_id = route.path_format
    operation_id = re.sub(r"\W", "_", operation_id)
    assert route.methods
    operation_id = operation_id + "_" + list(route.methods)[0].lower()
    # leading / generates a leading _ value.
    operation_id = re.sub("_$", "", re.sub("^_+", "", operation_id))
    return operation_id


def _use_route_names_as_operation_ids(application: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.

    This is to create client service names that are shorter and more readable.
    """
    # See https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration/?h=operation#using-the-path-operation-function-name-as-the-operationid
    route_operation_ids = set()
    for route in application.routes:  # type: ignore
        if isinstance(route, APIRoute):
            operation_id = _generate_operation_id(route)
            if operation_id in route_operation_ids:
                raise ValueError(f"Duplicate operation ID: {operation_id}")
            route_operation_ids.add(operation_id)
            route.operation_id = operation_id


_use_route_names_as_operation_ids(app)
