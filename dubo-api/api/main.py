from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from datadog import initialize

from api.handlers.api import router as api_router
from api.core.config import get_settings
from api.core.logging import get_logger
from api.core.stats import attach_stats_middleware, stats
from api.handlers.census import router as census_router
from api.handlers.api import router as api_router

app = FastAPI()

logger = get_logger(__name__)
settings = get_settings()
initialize(**settings.dd_init_kwargs)
attach_stats_middleware(app)

app.include_router(api_router, prefix="/v1")
app.include_router(census_router, prefix="/demos")


origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def _startup() -> None:
    stats.start()


@app.get("/health", tags=["health"])
async def health():
    logger.info("Health endpoint received request", extra={"endpoint": "health", "num": 123})
    return {"message": "OK"}


@app.get("/")
def read_root():
    return "Have no sphere - Copyright Mercator 2023"
