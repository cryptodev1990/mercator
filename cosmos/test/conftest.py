"""Common configuration for tests."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Return the test client"""
    return TestClient(app)
