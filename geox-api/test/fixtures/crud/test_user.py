from sqlalchemy import text

from app.crud.user import create_user
from app.db.session import SessionLocal, engine
from app.schemas import UserCreate


def test_create_user():
    with SessionLocal() as db_session:
        user_id = None
        try:
            user = UserCreate(
                name="test user",
                email="test+USER@mercator.tech",
                nickname="Test",
                email_verified=False,
                iss="mercator.tech",
                picture="test.png",
                locale="en-US",
                updated_at=None,
                sub_id="test",
                given_name="Test",
                family_name="User",
            )
            new_user = create_user(db=db_session, user=user)
            user_id = new_user.id
            assert new_user.id
            assert new_user.given_name == "Test"
        finally:
            if user_id:
                with engine.connect() as con, con.begin():
                    con.execute(
                        text("DELETE FROM users WHERE id = :user_id"),
                        {"user_id": user_id},
                    )
