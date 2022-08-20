"""Test misc Postgres database schema things."""
from app.db.session import SessionLocal

def test_app_user_role_exists():
    with SessionLocal() as session, session.begin():
        # check that not signed in as the app user
        assert session.execute("SELECT current_user != 'app_user'").scalar()
        # check that the app user exists - because there would be an error otherwise
        session.execute("SET LOCAL role app_user")
        assert session.execute("SELECT current_user = 'app_user'").scalar()

def test_app_user_role_has_permissions():
    """Check that the app_user role can read from the public schema.

    Specific tests in routes will really test/read write capabilities
    """
    with SessionLocal() as session, session.begin():
        session.execute("SET LOCAL role app_user")
        assert session.execute("SELECT count(*) FROM shapes").scalar() is not None
