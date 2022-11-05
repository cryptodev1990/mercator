# pylint: disable=duplicate-code
"""Functions run prior to starting celery workers."""
import logging

from sqlalchemy import text
from tenacity import retry
from tenacity.after import after_log
from tenacity.before import before_log
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_fixed

from app.db.engine import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init() -> None:
    """Initialize celeryworker."""
    try:
        with engine.begin() as conn:
            stmt = text("SELECT 1")
            conn.execute(stmt)
    except Exception as e:
        logger.error(e)
        raise e


def main() -> None:
    """Initialize celery workers."""
    logger.info("Initializing service")
    init()
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
