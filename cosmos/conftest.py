"""Pytest configuration file for the project."""
import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

root_dir = Path(__file__).parent.absolute()
sys.path.append(str(root_dir))

# Set the environment variable to indicate it is in testing mode
os.environ["APP_ENV"] = "test"
logger.info("Running as test environment")