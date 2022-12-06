"""Script run before starting tests."""
# Copied from https://raw.githubusercontent.com/tiangolo/full-stack-fastapi-postgresql/master/%7B%7Bcookiecutter.project_slug%7D%7D/backend/app/app/tests_pre_start.py
import logging

from sqlalchemy import text
from tenacity import retry
from tenacity.after import after_log
from tenacity.before import before_log
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_fixed

from app.core.logging import get_logger
from app.db.engine import engine

# pylint: disable=duplicate-code
logging.basicConfig(level=logging.INFO)
logger = get_logger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init() -> None:
    try:
        with engine.begin() as conn:
            stmt = text("SELECT 1")
            conn.execute(stmt)
    except Exception as e:
        logger.error(e)
        raise e


def main() -> None:
    logger.info("Initializing service")
    init()
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
