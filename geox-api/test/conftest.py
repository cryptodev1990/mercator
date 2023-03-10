"""Pytest configuration."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine

from app.db.engine import create_app_engine
from app.main import app


@pytest.fixture(scope="module")
def engine() -> Engine:
    return create_app_engine()
