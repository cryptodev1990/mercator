"""Miscellaneous Postgres helper functions."""
from email import policy

from sqlalchemy import text
from sqlalchemy.engine import Connection


def policy_exists(conn: Connection, tablename: str, policyname: str) -> bool:
    """Check that a postgres table policy exists."""
    stmt = text(
        "SELECT exists(select 1 from pg_policies where tablename = :tablename and policyname = :policyname)"
    )
    return bool(conn.execute(stmt).scalar())


def assert_policy_exists(conn: Connection, tablename: str, policyname: str) -> None:
    assert policy_exists(
        conn, tablename, policyname
    ), f"PG policy {policyname} on table {tablename} does not exist."
