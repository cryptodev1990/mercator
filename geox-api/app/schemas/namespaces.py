import datetime
from typing import Any, Dict, Optional

from pydantic import UUID4, Field

from .common import BaseModel

__all__ = ["Namespace", "NamespaceCreate", "NamespaceUpdate"]


class Namespace(BaseModel):
    """Namespace data."""

    id: UUID4
    name: str
    properties: Dict[str, Any]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    is_default: bool

    class Config:
        schema_extra = {
            "example": {
                "id": "07ed91ac-ee3c-49e1-9172-62edcdf3cc75",
                "name": "Metropolitan Statistical Areas",
                "properties": {"color": "red"},
                "created_at": "2022-10-10T17:33:28.009874",
                "updated_at": "2022-10-10T17:33:28.009874",
                "is_default": False,
            }
        }


class NamespaceCreate(BaseModel):
    """Data to create a new namespace."""

    name: str
    properties: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        schema_extra = {
            "example": {
                "name": "Metropolitan Statistical Areas",
                "properties": {"color": "red"},
            }
        }


class NamespaceUpdate(BaseModel):
    """Data to update an existing namespace."""

    name: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Metropolitan Statistical Areas (MSA)",
                "properties": {"color": "blue"},
            }
        }
