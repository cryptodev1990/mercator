import datetime
from typing import Optional

from pydantic import UUID4, Field

from app.schemas.common import BaseModel

# This is imported by __init__ with *
# Append all objects to exported in __all__
__all__ = ["Organization"]


class Organization(BaseModel):
    """Represents an Organization."""

    id: UUID4
    name: str = Field(..., description="Organization name")
    created_by_user_id: Optional[int] = Field(None)
    deleted_at: Optional[datetime.datetime] = Field(None)
    is_personal: bool = Field(False)
    s3_export_enabled: bool = Field(False)
    snowflake_account_id: Optional[str] = Field(None)
