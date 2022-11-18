"""FastAPI response schemes."""
from enum import Enum
from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel, NonNegativeFloat # pylint: disable=no-name-in-module
from pydantic import Field

from app.core.datatypes import BBoxTuple


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

    class_name: Optional[str] = None
    id_: Optional[int] = None
    bbox: Optional[BBoxTuple] = None


class SpRel(BaseModel):
    """A spatial relationship between geometries."""

    location: Optional[Location]


class SpRelIn(SpRel):
    """The spatial relationship A is covered by B."""

    type: Literal["in"]


class SpRelCrosses(SpRel):
    """The spatial relationship A crosses B."""

    type: Literal["crosses"]


class SpRelBorders(SpRel):
    """The spatial relationship A touches B."""

    type: Literal["borders"]


class CardinalDirections(str, Enum):
    """Cardinal directioons."""

    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"


class SpRelDirection(SpRel):
    """Spatial relationships for cardinal directions.

    For example: A is west of B.

    """

    type: Literal["direction"]
    direction: CardinalDirections


class SpRelDistance(SpRel):
    """Spatial relationships with distances."""

    type: Literal["distance"]
    relation: Literal[">", "<"] = Field("<")
    value: NonNegativeFloat = Field(..., description="Distance in meters")


class Modalities(str, Enum):
    """Modalalities used to calculate isochrones."""

    WALKING = "walking"
    DRIVING = "driving"
    CYCLING = "cycling"


class SpRelTime(SpRel):
    """Spatial relationship for the time to travel between two geometries."""
    type: Literal["time"]
    relation: Literal[">", "<"]
    value: NonNegativeFloat = Field(..., description="Time in seconds.")
    modality: Modalities = Field()


SpatialRelation = Annotated[
    Union[
        SpRelIn, SpRelDistance, SpRelCrosses, SpRelBorders, SpRelDistance, SpRelTime, SpRelDirection
    ],
    Field(discriminator="type"),
]
"""Union of all spatial relations.

The discriminator field is used to determine the type of the spatial relation.
"""


class LocationQuery(Location):
    """Location query parameters."""

    relations: List[SpatialRelation] = Field(default_factory=list)
    # TODO: allow locations in relations to be fully recursive and
    # have their own spatial relations
