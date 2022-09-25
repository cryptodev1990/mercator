from functools import partial
from typing import Any, AsyncGenerator, Callable, Dict, List

import pytest
from fastapi import Depends
from sqlalchemy import delete, insert, select
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session

from app import models
from app.schemas import User
from app.crud.organization import set_active_org
from app.db.session import SessionLocal, engine
from app.dependencies import get_current_user, get_session, verify_token
from app.main import app
from sqlalchemy.engine import Connection, Row  # type: ignore

org_tbl = models.Organization.__table__
org_mbr_tbl = models.OrganizationMember.__table__
shape_tbl = models.Shape.__table__
user_tbl = models.User.__table__


def get_user_orgs(db: Connection, user_id: int) -> List[Row]:
    stmt = select(
        org_tbl.c.id.label("organization_id"),  # type: ignore
        org_tbl.c.is_personal,
    ).join(org_mbr_tbl.c.organization.and_(org_mbr_tbl.c.user_id == user_id))
    return db.execute(stmt).fetchall()


@pytest.fixture()
def connection(test_data: Dict[str, Any]):
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            for tbl in (shape_tbl, org_mbr_tbl, org_tbl, user_tbl):
                conn.execute(delete(tbl))
            conn.execute(insert(user_tbl), test_data["users"])  # type: ignore
            conn.execute(insert(org_tbl), test_data["organizations"])  # type: ignore
            for org_member in test_data["organization_members"]:
                conn.execute(insert(org_mbr_tbl), org_member)  # type: ignore
                # Set these new organizations to the active organization
                set_active_org(
                    conn, org_member["user_id"], org_member["organization_id"]
                )
            conn.execute(insert(shape_tbl), test_data["shapes"])  # type: ignore

            yield conn
        finally:
            trans.rollback


def get_current_user_override(
    *, user_id: int, db_session: Session = Depends(get_session)
):
    """Return a particular existing user by id.

    This skips authentication of users to allow fake users.
    """
    user = db_session.execute(
        select(user_tbl).filter(user_tbl.c.id == user_id)  # type: ignore
    ).fetchone()
    return User.from_orm(user)


def get_session_override(
    conn: Connection,
) -> Callable[[], AsyncGenerator[Session, None]]:
    """Return a session bound to a particular connection."""
    # the session is bound to a connection that
    # already has an open
    async def f() -> AsyncGenerator[Session, None]:
        with SessionLocal(bind=conn) as session:
            yield session

    return f


@pytest.fixture()
def dep_override_factory(fastapi_dep, connection):
    """Return the common dependency overrides."""

    def overrides(user_id: int):
        return fastapi_dep(app).override(
            {
                get_session: get_session_override(connection),
                get_current_user: partial(get_current_user_override, user_id=user_id),
                verify_token: lambda: {},
            }
        )

    return overrides
