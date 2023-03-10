"""Custom Pydantic Data Types."""
import re
from enum import Enum
from typing import TYPE_CHECKING, Literal, Union

# pylint: disable=no-name-in-module
from pydantic import AnyHttpUrl, AnyUrl, ConstrainedFloat, ConstrainedStr, constr

# pylint: enable=no-name-in-module

AnyHttpURLorAsterisk = Union[AnyHttpUrl, Literal["*"]]
"""A valid HTTP URL or *."""
# used in CORS types


class AppEnvEnum(str, Enum):
    """Environment in which the app is being run."""

    prod = "production"
    production = "production"
    dev = "dev"
    test = "test"
    staging = "staging"

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


class S3Url(AnyUrl):
    """Validate an S3 URI type.

    Example: ``s3://bucket-name/path/to/file``.

    """

    allowed_schemes = {
        "s3",
    }
    host_required = True

    __slots__ = ()


class MapProjection(int, Enum):
    WGS84 = 4326
    WEB_MERCATOR = 3857


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


class Slug(ConstrainedStr):
    """Valid slug value."""

    regex = re.compile(r"^[a-z0-9_-]+$")
