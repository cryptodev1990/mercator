"""Main module of the app."""
import logging
import random
import string
import time

from fastapi import FastAPI, Request
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from app import routes
from app.core.config import get_settings
from app.middleware import ProtectedRoutesMiddleware

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
        Middleware(
            ProtectedRoutesMiddleware,
            protected_routes=["/protected_health", "/geofencer*"],
        ),
    ],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    idem = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    logger.info(f"rid={idem} start request path={request.url.path}")
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    formatted_process_time = "{0:.2f}".format(process_time)
    logger.info(
        f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}"
    )

    return response


app.include_router(routes.osm.router)
app.include_router(routes.health.router)
app.include_router(routes.shapes.router)
app.include_router(routes.tasks.router)
app.include_router(routes.info.router)


@app.get("/")
async def home():
    return "Have no sphere - Mercator, Inc 2022"
