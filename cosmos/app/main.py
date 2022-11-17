"""Fastapi main"""
import logging

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection  # type: ignore
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db import engine
from app.dependencies import get_conn
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
