"""Defines the base class for all models."""
# Copied from https://github.com/tiangolo/full-stack-fastapi-postgresql/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/backend/app/app/db/base_class.py
from sqlalchemy.ext.declarative import declarative_base

from .session import SessionLocal, engine

Base = declarative_base()

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


"""Base class which all models inherit from."""
