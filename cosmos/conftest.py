"""Pytest configuration file for the project."""
import pytest
from fastapi.testclient import TestClient


import asyncio

import logging
import os
import sys
from pathlib import Path
from app.main import app

import pytest_asyncio

logger = logging.getLogger(__name__)

root_dir = Path(__file__).parent.absolute()
sys.path.append(str(root_dir))

# Set the environment variable to indicate it is in testing mode
os.environ["APP_ENV"] = "TEST"
logger.info("Running as test environment")

@pytest_asyncio.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()