"""Custom Pydantic Data Types."""
from typing import TYPE_CHECKING, Union, Literal
from pydantic import AnyHttpUrl, AnyUrl, ConstrainedFloat, constr


AnyHttpURLorAsterisk = Union[AnyHttpUrl, Literal["*"]]
"""A valid HTTP URL or *."""
# used in CORS types

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
