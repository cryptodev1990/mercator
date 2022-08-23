import pytest

from app.db.app_user import get_app_user_id, set_app_user_id, unset_app_user_id
from app.db.session import SessionLocal


@pytest.fixture(scope="function")
def db_session():
    with SessionLocal() as session:
        yield session


def test_set_app_user_id(db_session):
    """Test setting and unsetting app user."""
    user_id = "1234"
    set_app_user_id(db_session, user_id)
    assert get_app_user_id(db_session) == user_id
    unset_app_user_id(db_session)
    assert get_app_user_id(db_session) is None


def test_get_app_user_id_when_none_set(db_session):
    """Test setting and unsetting app user."""
    assert get_app_user_id(db_session) is None


def test_check_app_auth_user_ids_parallel_sessions():
    """Test setting and unsetting app user."""
    with SessionLocal() as session1, SessionLocal() as session2:
        user_id_1 = "1234"
        user_id_2 = "5678"
        set_app_user_id(session1, user_id_1)
        assert get_app_user_id(session1) == user_id_1
        assert get_app_user_id(session2) is None
        set_app_user_id(session2, user_id_2)
        assert get_app_user_id(session1) == user_id_1
        assert get_app_user_id(session2) == user_id_2
        unset_app_user_id(session1)
        assert get_app_user_id(session1) is None
        assert get_app_user_id(session2) == user_id_2
        unset_app_user_id(session2)
        assert get_app_user_id(session1) is None
        assert get_app_user_id(session2) is None


def test_check_app_auth_user_ids_nested_sessions():
    """Test setting and unsetting app user."""
    user_id_1 = "1234"
    user_id_2 = "5678"
    with SessionLocal() as session1:
        set_app_user_id(session1, user_id_1)
        with SessionLocal() as session2:
            assert get_app_user_id(session1) == user_id_1
            assert get_app_user_id(session2) is None
            set_app_user_id(session2, user_id_2)
            assert get_app_user_id(session1) == user_id_1
            assert get_app_user_id(session2) == user_id_2
            unset_app_user_id(session1)
            assert get_app_user_id(session1) is None
            assert get_app_user_id(session2) == user_id_2
            unset_app_user_id(session2)
            assert get_app_user_id(session1) is None
            assert get_app_user_id(session2) is None


def test_check_app_auth_user_ids_sequential_sessions():
    """Check settings when no cleanup"""
    user_id_1 = "1234"
    with SessionLocal() as session1:
        assert get_app_user_id(session1) is None
        set_app_user_id(session1, user_id_1)
        assert get_app_user_id(session1) == user_id_1
    with SessionLocal() as session2:
        assert get_app_user_id(session2) is None
