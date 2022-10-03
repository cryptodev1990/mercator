"""App users."""
import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Table

from app.db.metadata.common import metadata

__all__ = ["users"]

users = Table("users"
    , metadata
    , Column("id", Integer, primary_key=True, index=True)
    , Column("sub_id", String, unique=True, index=True)
    , Column("email", String, unique=True, index=True)
    , Column("is_active", Boolean, default=True)
    , Column("given_name", String)
    , Column("family_name", String)
    , Column("nickname", String)
    , Column("name", String)
    , Column("picture", String)
    , Column("locale", String)
    , Column("updated_at", DateTime, default=datetime.datetime.utcnow)
    , Column("email_verified", Boolean)
    , Column("iss", String)
    , comment = "Represents a user of the app.")