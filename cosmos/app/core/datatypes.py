# pylint: disable=too-few-public-methods
"""Custom Pydantic Data Types."""
from enum import Enum
from typing import TYPE_CHECKING, Any, Sequence, Tuple

# pylint: disable=no-name-in-module
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConstrainedFloat, Field, constr, root_validator

# pylint: enable=no-name-in-module


class BaseModel(PydanticBaseModel):
    """Local BaseModel class to add common functionality."""


class AppEnvEnum(str, Enum):
    """Environment in which the app is being run."""

    PROD = "PROD"
    DEV = "DEV"
    TEST = "TEST"
    STAGING = "STAGING"

    def __str__(self) -> str:
        return str(self.value)


class LogLevel(str, Enum):
    """Python logging module log level constants represented as an ``enum.Enum``."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    def __str__(self) -> str:
        return str(self.value)


if TYPE_CHECKING:
    GitCommitHash = str
else:
    GitCommitHash = constr(
        min_length=40,
        max_length=40,
        regex="^[0-9a-fA-F]{40}$",
        strict=True,
        to_lower=True,
        strip_whitespace=True,
    )
    """Pydantic type to validate git hashes."""


if TYPE_CHECKING:
    Latitude = float
    Longitude = float
else:

    class Latitude(ConstrainedFloat):
        """Latitude Data Type."""

        ge = -90
        le = 90

    class Longitude(ConstrainedFloat):
        """Longitude Data Type."""

        ge = -180
        le = 180


class ViewportBounds(BaseModel):
    """Bounding box."""

    min_x: Longitude = Field(..., description="Minimum X coordinate")
    min_y: Latitude = Field(..., description="Minimum Y coordinate")
    max_x: Longitude = Field(..., description="Maximum X coordinate")
    max_y: Latitude = Field(..., description="Maximum Y coordinate")

    # validate that the minimums are less than the maximums
    # pylint: disable=no-self-argument
    @root_validator()
    def _validate_min_max(cls, value: Any) -> Any:
        if value["min_x"] > value["max_x"]:
            raise ValueError("min_x must be less than max_x")
        if value["min_y"] > value["max_y"]:
            raise ValueError("min_y must be less than max_y")
        return value

    # pylint: enable=no-self-argument

    # pylint: disable=no-self-argument
    @classmethod
    def from_list(cls, coordinates: Sequence[float]) -> "ViewportBounds":
        """Create a viewport from a list of coordinates."""
        if len(coordinates) != 4:
            raise ValueError("Four coordinates must be provided.")
        min_x, min_y, max_x, max_y = coordinates
        return cls(min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y)

    # pylint: enable=no-self-argument


BBoxTuple = Tuple[Longitude, Latitude, Longitude, Latitude]
"""Bounding box as a tuple of floats."""
