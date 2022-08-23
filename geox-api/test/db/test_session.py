"""Test functionality in app.db.session."""
import sqlalchemy as sa

from app.db.session import SessionLocal, engine


def test_app_auth_user_id_default():
    """The setting app.user_id is set.
    This will throw an error if it is not.
    """
    with engine.connect() as conn:
        res = conn.execute(sa.text("SELECT current_setting('app.user_id')")).scalar()
    assert res == ""


def test_app_auth_user_id_default_in_session():
    """The setting app\.user_id is set."""
    with SessionLocal() as session:
        res = session.execute(sa.text("SELECT current_setting('app.user_id')")).scalar()
    assert res == ""


def test_app_auth_user_id_reset_conn():
    """Test that app.user_id settings do not persist across sessions and connections."""
    for _ in range(20):
        with engine.connect() as conn, conn.begin():
            assert (
                conn.execute(sa.text("SELECT current_setting('app.user_id')")).scalar()
                == ""
            )
            conn.execute(sa.DDL("SET app.user_id = '1'"))
            assert (
                conn.execute(sa.text("SELECT current_setting('app.user_id')")).scalar()
                == "1"
            )


def test_app_auth_user_id_reset():
    """Test that app.user_id settings do not persist across sessions and connections."""
    for _ in range(20):
        with SessionLocal() as session:
            with session.begin():
                assert (
                    session.execute(
                        sa.text("SELECT current_setting('app.user_id')")
                    ).scalar()
                    == ""
                )
                session.execute(sa.DDL("SET app.user_id = '1'"))
                assert (
                    session.execute(
                        sa.text("SELECT current_setting('app.user_id')")
                    ).scalar()
                    == "1"
                )
