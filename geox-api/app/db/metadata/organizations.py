from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.metadata.common import TimestampMixin, UUIDMixin, metadata

__all__ = ["organizations", "organization_members"]

organizations = Table(
    "organizations",
    metadata,
    *UUIDMixin(),
    Column("name", String, nullable=False),
    Column(
        "created_by_user_id",
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    ),
    Column("deleted_at", DateTime),
    Column("is_personal", Boolean, default=False),
    Column(
        "s3_export_enabled",
        Boolean,
        default=False,
        nullable=False,
        comment="Allow exporting data to S3.",
    ),
    Column(
        "snowflake_account_id",
        String,
        comment="Snowflake Account ID. Used for data export. See https://docs.snowflake.com/en/user-guide/admin-account-identifier.html.",
    ),
    Column("stripe_subscription_id", String, nullable=True),
    Column("stripe_subscription_created_at", DateTime, nullable=True),
    Column("stripe_paid_at", DateTime, nullable=True),
    Column("subscription_whitelist", Boolean, nullable=False, default=False),
    Column("stripe_subscription_status", String, nullable=True),
    *TimestampMixin(),
    comment="An organization is a collection of members.",
)


organization_members = Table(
    "organization_members",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    ),  # https://stackoverflow.com/questions/5033547/sqlalchemy-cascade-delete
    Column(
        "organization_id",
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column(
        "added_by_user_id",
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    ),
    Column("active", Boolean, default=False, nullable=False),
    Column("deleted_at", DateTime, nullable=True),
    *TimestampMixin(),
    UniqueConstraint("user_id", "organization_id"),
    comment="Represents membership in an organization.",
)
