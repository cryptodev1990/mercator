"""Test functions in app.dependencies."""
import pytest
from sqlalchemy import text

from app import schemas
from app.db.app_user import get_app_user_id
from app.db.session import SessionLocal, engine
from app.dependencies import get_app_user_session


@pytest.fixture
def user():
    return schemas.User(email="tester@example.com", id=1234, sub_id=5, is_active=True)


@pytest.mark.asyncio
async def test_get_auth_user_session(user):
    """
    Test setting app.auth_user_id setting in sessions.

    These are some basic test to check that the value is only set within
    the session, and not in other sessions.

    """
    # Replace all dependencies with actual objects
    with SessionLocal() as session, SessionLocal() as other_session:
        with session.begin():
            # app.auth_user_id is empty
            assert get_app_user_id(session) is None
            assert get_app_user_id(other_session) is None
        # Add lisetning events to the session
        user_session = await get_app_user_session(user, session)
        assert user_session.session == session
        # Now app.auth_user_id is set
        with session.begin():
            assert get_app_user_id(session) == str(user.id)
            assert get_app_user_id(other_session) is None
        with session.begin():
            assert get_app_user_id(session) == str(user.id)
            assert get_app_user_id(other_session) is None
        # implicit BEGIN
        assert get_app_user_id(session) == str(user.id)
        # Did not change the setting in the other session
        assert get_app_user_id(other_session) is None
        try:
            session.execute(text("This is an error"))
        except:
            pass
        assert get_app_user_id(other_session) is None
        session.rollback()
    # Check that new sessions are unaffected
    for _ in range(10):
        with SessionLocal() as session:
            assert get_app_user_id(other_session) is None
    for _ in range(10):
        with engine.connect() as conn:
            assert get_app_user_id(conn) is None
