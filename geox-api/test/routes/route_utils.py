from functools import partial
from typing import Any, Dict

import pytest
from fastapi import Depends
from pydantic import UUID4
from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session
from app.models import Shape

from app import models, schemas
from app.db.base import Organization, OrganizationMember, User
from app.db.session import SessionLocal, engine
from app.dependencies import get_current_user, get_db, verify_token
from app.main import app
from app.crud.organization import set_active_org


@pytest.fixture()
def connection(test_data: Dict[str, Any]):
    with engine.connect() as conn:
        with conn.begin():
            for tbl in (Shape.__table__, OrganizationMember.__table__, Organization.__table__, User.__table__):
                conn.execute(delete(tbl))  # type: ignore
            conn.execute(insert(User.__table__), test_data["users"])  # type: ignore
            conn.execute(
                insert(Organization.__table__), test_data["organizations"]
            )  # type: ignore
            for org_member in test_data["organization_members"]:
                conn.execute(insert(OrganizationMember.__table__),
                             org_member)  # type: ignore
                # Set these new organizations to the active organization
                set_active_org(
                    conn, org_member["user_id"], org_member["organization_id"]
                )
            conn.execute(insert(Shape.__table__), test_data["shapes"])  # type: ignore
            conn.commit()

        yield conn

        # Can't trust routes to handle their transactions correctly so close any open
        # transactions
        try:
            conn.commit()
        except:
            pass

        with conn.begin():
            for tbl in (Shape.__table__, OrganizationMember.__table__, Organization.__table__, User.__table__):
                conn.execute(delete(tbl))  # type: ignore
            conn.commit()


def get_current_user_override(*, user_id: int, db_session: Session = Depends(get_db)):
    """Return a particular existing user by id.

    This skips authentication of users to allow fake users.
    """
    user = db_session.execute(
        select(models.User).filter(models.User.id == user_id)  # type: ignore
    ).fetchone()
    return schemas.User.from_orm(user[0])


def get_db_override(connection):
    def f():
        db = SessionLocal(bind=connection)
        try:
            yield db
            try:
                db.commit()
            except:
                pass
        finally:
            db.close()

    return f


@pytest.fixture()
def dep_override_factory(fastapi_dep, connection):
    """Return the common dependency overrides."""

    def overrides(user_id: int):
        return fastapi_dep(app).override(
            {
                get_db: get_db_override(connection),
                get_current_user: partial(get_current_user_override, user_id=user_id),
                verify_token: lambda: {},
            }
        )

    return overrides
