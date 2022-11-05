# pylint: disable=redefined-outer-name
from test.crud.common import insert_test_users_and_orgs
from typing import Generator

import pytest
from sqlalchemy.engine import Connection


@pytest.fixture(scope="function")
def conn(engine) -> Generator[Connection, None, None]:
    conn = engine.connect()
    trans = conn.begin()
    try:
        insert_test_users_and_orgs(conn)
        yield conn
    finally:
        trans.rollback()
        conn.close()


# def test_set_organization_billing_profile_from_email(conn: Connection):
#     """Test that the organization's billing profile is set correctly."""
