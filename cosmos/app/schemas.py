"""FastAPI response schemes."""
from enum import Enum
from typing import Annotated, Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

from app.core.datatypes import BBox, FeatureCollection


class Schema(BaseModel):
    """Base schema class."""


class HealthStatus(str, Enum):
    """Helath status codes."""

    OK = "OK"
    ERROR = "ERROR"


class HealthResponse(BaseModel):
    """Health response model."""

    message: HealthStatus


class Location(BaseModel):
    """A location in a location query.

    The full location query also can include spatial relations.

    """

    query: Optional[str] = None
    bbox: Optional[BBox] = None


class SpRel(BaseModel):
    """A spatial relationship between geometries."""

    location: Optional[Location]


class SpRelContains(SpRel):
    """The spatial relationship A is covered by B."""

    type: Literal["contains"] = "contains"


class SpRelCoveredBy(SpRel):
    """The spatial relationship A is covered by B."""

    type: Literal["covered_by"] = "covered_by"


class SpRelDisjoint(SpRel):
    """The spatial relationship A is covered by B."""

    type: Literal["disjoint"] = "disjoint"


SpatialRelation = Annotated[
    Union[SpRelContains, SpRelDisjoint, SpRelCoveredBy],
    Field(discriminator="type"),
]
"""Union of all spatial relations.

The discriminator field is used to determine the type of the spatial relation.
"""

OsmQueryParse = Dict[str, Any]
"""Represents information about the parsed query."""


class OsmSearchResponse(BaseModel):
    """Response for OSM search."""

    query: str
    label: Optional[str] = None
    parse: Optional[OsmQueryParse] = None
    results: FeatureCollection = Field(default_factory=lambda: FeatureCollection.parse_obj({}))


class OsmRawQueryResponse(BaseModel):
    """Response for raw SQL executed against OSM."""

    query: str
    results: List[Dict[str, Any]]
