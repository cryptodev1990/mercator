"""Initialize the app database."""

from sqlalchemy.engine import Connection

# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28

# pylint: disable=unused-argument
def init_db(conn: Connection) -> None:
    """Initialize the app database."""
