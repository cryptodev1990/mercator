"""Defines the base class for all models."""
# Copied from https://github.com/tiangolo/full-stack-fastapi-postgresql/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/backend/app/app/db/base_class.py
from sqlalchemy.orm import declarative_base # type: ignore

from .session import engine

Base = declarative_base()

Base.metadata.create_all(bind=engine)
