"""SQLAlchemy session objects and functions."""

from typing import Any, Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import get_settings

SQLALCHEMY_DATABASE_URI: Any = get_settings().sqlalchemy_database_uri

engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
"""SQLALchemy session to use in the app."""


def get_db() -> Generator[Session, None, None]:
    """Yield a session.

    This function is designed to be used with `FastAPI dependency injection <https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/>`__.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
