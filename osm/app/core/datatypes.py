# pylint: disable=too-few-public-methods
"""Custom Pydantic Data Types."""
from enum import Enum
from typing import TYPE_CHECKING

# pylint: disable=no-name-in-module
from pydantic import ConstrainedFloat, constr

# pylint: enable=no-name-in-module


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
