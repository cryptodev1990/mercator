"""Database credentials model"""
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship

from app.models.common import TimestampMixin, UUIDMixin
from app.models.organization import Organization
from app.models.user import User


class DbCredential(UUIDMixin, TimestampMixin):
    __tablename__ = "db_credentials"

    name = Column(String, index=True, nullable=False)
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
    )
    is_default = Column(Boolean, default=False, nullable=False)
    created_by_user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    updated_by_user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    db_driver = Column(String, nullable=False)
    # DB credentials - encrypted
    db_user = Column(String, nullable=False)
    db_password = Column(String, nullable=False)
    db_host = Column(String, nullable=False)
    db_port = Column(String, nullable=False)
    db_database = Column(String, nullable=False)
    db_extras = Column(String, nullable=True)

    organization = relationship(
        "Organization",
        backref=backref(
            "OrganizationMember", passive_deletes=True, cascade="all,delete"
        ),
        foreign_keys=[organization_id],
    )
    created_by_user = relationship(User, foreign_keys=[created_by_user_id])
    updated_by_user = relationship(User, foreign_keys=[updated_by_user_id])

    UniqueConstraint("name", "organization_id", name="unique_within_org")
