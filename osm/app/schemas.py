"""FastAPI response schemes."""

from enum import Enum

from pydantic import BaseModel # pylint: disable=no-name-in-module


class Schema(BaseModel):
    """Base schema class."""


class HealthStatus(str, Enum):
    """Helath status codes."""

    OK = "OK"
    ERROR = "ERROR"


class HealthResponse(BaseModel):
    """Health response model."""

    message: HealthStatus
