"""Miscellaneous Postgres helper functions."""
import random
from string import ascii_letters, digits

from sqlalchemy import text
from sqlalchemy.engine import Connection


def policy_exists(conn: Connection, tablename: str, policyname: str) -> bool:
    """Check that a postgres table policy exists."""
    stmt = text(
        "SELECT exists(select 1 from pg_policies where tablename = :tablename and policyname = :policyname)"
    )
    return bool(
        conn.execute(stmt, {"tablename": tablename, "policyname": policyname}).scalar()
    )


def assert_policy_exists(conn: Connection, tablename: str, policyname: str) -> None:
    assert policy_exists(
        conn, tablename, policyname
    ), f"PG policy {policyname} on table {tablename} does not exist."


_ASCII_ALPHANUMERIC = ascii_letters + digits


def random_sub_id():
    prefix = "".join([random.choice(_ASCII_ALPHANUMERIC) for i in range(32)])
    return f"{prefix}@clients"
