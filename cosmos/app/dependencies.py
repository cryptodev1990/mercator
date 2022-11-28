"""FastAPI dependencies.

See `FastAPI dependency injection <https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/>`__.
"""
import logging
from functools import lru_cache
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.ext.asyncio import AsyncEngine  # type: ignore

from app.db import create_app_engine

logger = logging.getLogger(__name__)


@lru_cache()
def get_engine() -> AsyncEngine:
    """Return an engine to generate connections to the app database."""
    return create_app_engine()


async def get_conn(
    engine: Engine = Depends(get_engine),
) -> AsyncGenerator[Connection, None]:
    """Yield a connection with an open transaction."""
    # engine.begin() yields a connection and also opens a transaction.
    # the context manager will close the connection and transaction
    async with engine.begin() as conn:  # type: ignore
        yield conn
