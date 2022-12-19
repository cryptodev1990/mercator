"""Structured data to represent the intents that voyager supports.

The quantity and format of these intents is subject to change.

"""
import logging
from typing import Any, Dict

from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class _LocalModel(BaseModel):
    """Local pydantic model for this module."""

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True


class OpenAIDerivedIntent(_LocalModel):
    intent: Any  # TODO how to get the intent class here?
    args: Dict[str, Any]

    def __str__(self) -> str:
        return str(self.intent)


class ParsedQuery(_LocalModel):
    """Parse of a query."""

    value: OpenAIDerivedIntent = Field(..., description="Query intent")
    text: str

    def __str__(self) -> str:
        return str(self.value)
