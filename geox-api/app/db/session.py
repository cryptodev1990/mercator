"""SQLAlchemy session objects and functions."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

SQLALCHEMY_DATABASE_URI = get_settings().sqlalchemy_database_uri

engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
"""SQLALchemy session to use in the app."""
