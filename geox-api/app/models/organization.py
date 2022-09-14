from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship

from app.db.base_class import Base
from app.models.common import TimestampMixin, UUIDMixin
from app.models.user import User


class Organization(TimestampMixin, UUIDMixin, Base):
    """An organization is a collection of members."""

    __tablename__ = "organizations"

    name = Column(String, nullable=False)
    created_by_user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    deleted_at = Column(DateTime)
    is_personal = Column(Boolean, default=False)
    s3_export_enabled = Column(
        Boolean, default=False, nullable=False, comment="Allow exporting data to S3."
    )
    snowflake_account_id = Column(
        String,
        comment="Snowflake Account ID. Used for data export. See https://docs.snowflake.com/en/user-guide/admin-account-identifier.html.",
    )

    user = relationship(
        "User",
        backref=backref("Organization", passive_deletes=True, cascade="all,delete"),
        foreign_keys=[created_by_user_id],
    )


class OrganizationMember(TimestampMixin, Base):
    """Represents membership in an organization."""

    __tablename__ = "organization_members"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    # https://stackoverflow.com/questions/5033547/sqlalchemy-cascade-delete
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    added_by_user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    active = Column(Boolean, default=False, nullable=False)

    # https://stackoverflow.com/questions/7548033/how-to-define-two-relationships-to-the-same-table-in-sqlalchemy
    user = relationship(
        User,
        backref=backref(
            "OrganizationMember", passive_deletes=True, cascade="all,delete"
        ),
        foreign_keys=[user_id],
    )
    added_by_user = relationship("User", foreign_keys=[added_by_user_id])
    deleted_at = Column(DateTime, nullable=True)
    organization = relationship("Organization", foreign_keys=[organization_id])
    UniqueConstraint("user_id", "organization_id")
