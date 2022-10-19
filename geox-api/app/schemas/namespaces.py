import datetime
import re
from typing import Any, Dict, List, Optional

from pydantic import UUID4, Field, validator
from slugify import slugify

from app.core.datatypes import Slug

from .common import BaseModel
from .shape import GeoShapeMetadata

__all__ = ["Namespace", "NamespaceCreate", "NamespaceUpdate"]


class Namespace(BaseModel):
    """Namespace data."""

    id: UUID4
    name: str
    slug: Slug
    properties: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime.datetime
    updated_at: datetime.datetime
    is_default: bool

    shapes: Optional[List[GeoShapeMetadata]] = Field(
        default_factory=list,
        description="""
        List of shape metadata of shapes in the namespace.
        None means that shape metadata wasn't requested.
        An empty list means that there are no shapes.""",
    )


def not_default(v: str) -> str:
    """Check string is not equal to 'default'."""
    if v.lower() == "default":
        raise ValueError("Cannot equal 'default'")
    return v


def normalize_name(v: str) -> str:
    """Normalize name fields.

    Remove leading/training whitespace.
    """
    return v.strip()


class NamespaceCreate(BaseModel):
    """Data to create a new namespace."""

    name: str
    _validate_normalize_name = validator("name", allow_reuse=True)(normalize_name)
    _validate_name_not_default = validator("name", allow_reuse=True)(not_default)

    properties: Dict[str, Any] = Field(default_factory=dict)


class NamespaceUpdate(BaseModel):
    """Data to update an existing namespace."""

    name: str
    _validate_normalize_name = validator("name", allow_reuse=True)(normalize_name)
    _validate_name_not_default = validator("name", allow_reuse=True)(not_default)

    properties: Optional[Dict[str, Any]] = None
