"""Common classes used by the SQL tables."""
from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime, MetaData, func
from sqlalchemy.dialects.postgresql import UUID

__all__ = ["metadata"]

metadata = MetaData()

def TimestampMixin() -> List[Column]:
    return [
        Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
        Column(
            "updated_at",
            DateTime,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
            nullable=False,
        ),
    ]


def UUIDMixin() -> List[Column]:
    """UUID columns."""
    return [
        Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=func.gen_random_uuid(),
        )
    ]
