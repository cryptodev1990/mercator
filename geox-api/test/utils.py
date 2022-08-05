import datetime

from app import schemas
from app.crud.user import create_user


def make_user(db, test_email):
    new_user = schemas.UserCreate(
        email=test_email,
        given_name="Test",
        family_name="User",
        name="testuser",
        nickname="testuser",
        email_verified=True,
        iss="https://mercator.tech",
        sub_id="testuser",
        picture="https://mercator.tech/testuser.png",
        locale="en-US",
        updated_at=datetime.datetime.utcnow(),
    )
    create_user(db, new_user)
