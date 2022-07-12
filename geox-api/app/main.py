import logging
import os
import random
import string
import time

from fastapi import FastAPI, Request
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from .middleware import ProtectedRoutesMiddleware

from .routes import (
    health,
    shapes,
    tasks,
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


secret_key = os.environ["APP_SECRET_KEY"]

app = FastAPI(
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(
            ProtectedRoutesMiddleware,
            protected_routes=["/protected_health", "/geofencer*"],
        ),
    ]
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    idem = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    logger.info(f"rid={idem} start request path={request.url.path}")
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    logger.info(f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}")
    
    return response



app.include_router(health.router)
app.include_router(tasks.router)
app.include_router(shapes.router)


@app.get("/")
async def home():
    return "Have no sphere - Mercator, Inc 2022"
