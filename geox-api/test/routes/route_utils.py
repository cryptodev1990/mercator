from functools import partial
from typing import Any, AsyncGenerator, Callable, Dict

import pytest
from fastapi import Depends
from sqlalchemy import delete, insert, select
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session

from app import models, schemas
from app.crud.organization import set_active_org
from app.db.base import Organization, OrganizationMember, User
from app.db.session import SessionLocal, engine
from app.dependencies import get_current_user, get_session, verify_token
from app.main import app
from app.models import Shape


@pytest.fixture()
def connection(test_data: Dict[str, Any]):
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            for tbl in (Shape, OrganizationMember, Organization, User):
                conn.execute(delete(tbl))
            conn.execute(insert(User), test_data["users"])  # type: ignore
            conn.execute(
                insert(Organization), test_data["organizations"]
            )  # type: ignore
            for org_member in test_data["organization_members"]:
                conn.execute(insert(OrganizationMember), org_member)  # type: ignore
                # Set these new organizations to the active organization
                set_active_org(
                    conn, org_member["user_id"], org_member["organization_id"]
                )
            conn.execute(insert(Shape), test_data["shapes"])  # type: ignore

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
        select(models.User).filter(models.User.id == user_id)  # type: ignore
    ).fetchone()
    return schemas.User.from_orm(user[0])


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
