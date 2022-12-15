"""Structured data to represent the intents that voyager supports.

The quantity and format of these intents is subject to change.

"""
import logging
from datetime import timedelta
from enum import Enum
from typing import Any, Dict, List, Literal, Union

from pint import Quantity
from pydantic import BaseModel, Field
from app.models.intent import Intent  # pylint: disable=no-name-in-module

from app.parsers.time import readable_duration

logger = logging.getLogger(__name__)


def _quantity_to_dict(quantity: Quantity) -> dict[str, Any]:
    return {"magnitude": quantity.magnitude, "units": str(quantity.units)}


class _LocalModel(BaseModel):
    """Local pydantic model for this module."""

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True
        custom_encoders = {Quantity: _quantity_to_dict}


# pylint: disable=invalid-name
class TravelMethod(str, Enum):
    """Travel methods used in isochrones.

    These will need to be mapped to profiles in the routing engine.
    Whether the specificity of the profile is determined at parse time
    or later is TBD.

    """

    drive = "drive"
    walk = "walk"
    bike = "bike"


# pylint: enable=invalid-name


class Place(_LocalModel):
    """Represents a place.

    Examples:

    - coffee shops

    """

    # NOTE: the Literal[...] = Field(...) is redundant, but it seems to be needed to get
    # Field(..., discriminator=...) to work.
    type: Literal["place"] = Field("place", const=True)
    value: List[str]

    def __str__(self) -> str:
        return " ".join(self.value)


class NamedPlace(_LocalModel):
    """Named place.

    Examples:

    - "Los Angeles"
    - "San Francisco"
    - "Salesforce Tower"

    """

    type: Literal["named_place"] = Field("named_place", const=True)
    value: List[str]

    def __str__(self) -> str:
        return " ".join(self.value)


class _SpatialRelationship(_LocalModel):
    subject: Union[Place, NamedPlace]
    object: Union[Place, NamedPlace]


class SpRelCoveredBy(_SpatialRelationship):
    """Spatial relationship of X is covered by Y.

    Examples:

    - "Coffee shops in San Francisco"
    - "[place or named place] in [place or named place]"

    """

    type: Literal["covered_by"] = Field("covered_by", const=True)

    def __str__(self) -> str:
        return " ".join([str(self.subject), "IN", str(self.object)])


class SpRelDisjoint(_SpatialRelationship):
    """Spatial relationship of X disjoint Y.

    Examples:

    - "Coffee shops not in San Francisco"
    - "[place or named place] not in [place or named place]"

    """

    type: Literal["disjoint"] = Field("disjoint", const=True)

    def __str__(self) -> str:
        return " ".join([str(self.subject), "NOT IN", str(self.object)])


class SpRelWithinDistOf(_SpatialRelationship):
    """Spatial relationship of X within D distance of Y.


    Examples:

    - "Coffee shops within 20 miles of San Francisco"
    - "[place or named place] within [distance] of [place or named place]"

    Allowed distances are meters, miles, kilometers, yards, and feet.

    """

    type: Literal["within_dist_of"] = Field("within_dist_of", const=True)
    distance: float = Field(..., ge=0, description="Distance in meters")

    def __str__(self) -> str:
        return " ".join(
            [
                str(self.subject),
                "WITHIN",
                str(Quantity(self.distance, "meters").to("miles")),
                "FROM",
                str(self.object),
            ]
        )


class SpRelOutsideDistOf(_SpatialRelationship):
    """Spatial relationship of X more than D distance of Y.

    Examples:

    - "Coffee shops within 20 miles of San Francisco"
    - "[place or named place] outside of [distance] of [place or named place]"

    Allowed distances are meters, miles, kilometers, yards, and feet.

    """

    type: Literal["outside_dist_of"] = Field("outside_dist_of", const=True)
    distance: float = Field(..., ge=0, description="Distance in meters")

    def __str__(self) -> str:
        return " ".join(
            [
                str(self.subject),
                "NOT WITHIN",
                str(Quantity(self.distance, "meters").to("miles")),
                "OF",
                str(self.object),
            ]
        )


NEAR_DISTANCE = 1609.344
"""Constant used to determine the distance between two objects that is near."""


class SpRelNear(_SpatialRelationship):
    """Spatial relationship of X near Y.

    Examples:

    - "Coffee shops near parks"
    - "[place or named place] near [place or named place]"

    The distance at which two objects are near is defined by the cosntant `NEAR_DISTANCE`.

    """

    type: Literal["near"] = Field("near", const=True)
    distance: float = Field(NEAR_DISTANCE, ge=0, description="Distance in meters")

    def __str__(self) -> str:
        return " ".join([str(self.subject), "NEAR", str(self.object)])


class SpRelNotNear(_SpatialRelationship):
    """Spatial relationship of X not near Y.

    Examples:

    - "Coffee shops not near parks"
    - "[place or named place] not near [place or named place]"

    """

    type: Literal["not_near"] = Field("not_near", const=True)
    distance: float = Field(NEAR_DISTANCE, ge=0, description="Distance in meters")

    def __str__(self) -> str:
        return " ".join([str(self.subject), "NOT NEAR", str(self.object)])


class SpRelWithinTimeOf(_SpatialRelationship):
    """Spatial relationship of X within D time of Y.

    Examples:

    - "Coffee shops within 20 minutes of the Salesforce Tower"
    - "[place or named place] within [time] of [place or named place]"

    """

    type: Literal["within_time_of"] = Field("within_time_of", const=True)
    duration: timedelta
    method: TravelMethod = TravelMethod.drive

    def __str__(self) -> str:
        return " ".join(
            [str(self.subject), "WITHIN", str(self.duration), "OF", str(self.object)]
        )


class SpRelOutsideTimeOf(_SpatialRelationship):
    """Spatial relationship of X greater than D time from Y.

    Examples:

    - "Coffee shops not within 20 minutes of the Salesforce Tower"
    - "[place or named place] not within [time] of [place or named place]"

    """

    type: Literal["outside_time_of"] = Field("outside_time_of", const=True)
    duration: timedelta
    profile: TravelMethod = Field(
        TravelMethod.drive, description="Isochrone profile used in the calculation."
    )

    def __str__(self) -> str:
        return " ".join(
            [
                str(self.subject),
                "MORE THAN",
                readable_duration(self.duration),
                "FROM",
                str(self.object),
            ]
        )


class Buffer(_LocalModel):
    """Buffer around object.

    Examples:

    - "Buffer of 20 miles around the Salesforce Tower"
    - "Buffer of [time] round [place or named place]"

    """

    type: Literal["buffer"] = Field("buffer", const=True)
    object: Union[Place, NamedPlace]
    distance: float = Field(..., ge=0, description="Distance in meters")

    def __str__(self) -> str:
        return " ".join(
            ["BUFFER OF", str(Quantity(self.distance, "miles")), "AROUND", str(self.object)]
        )


class Isochrone(_LocalModel):
    """Isochrone around an object.

    Examples:

    - "Buffer of 20 minutes around the Salesforce Tower"
    - "Buffer of [time] around [place or named place]"

    """

    type: Literal["isochrone"] = Field("isochrone", const=True)
    object: Union[Place, NamedPlace]
    duration: timedelta
    profile: TravelMethod = Field(
        TravelMethod.drive, description="Isochrone profile used in the calculation."
    )

    def __str__(self) -> str:
        return " ".join(
            ["BUFFER OF", readable_duration(self.duration), "AROUND", str(self.object)]
        )


class Route(_LocalModel):
    """Route between two places.

    Examples:

    - "Route from San Francisco to San Jose"
    - "Route from [named place] to [named place]"

    """

    type: Literal["route"] = Field("route", const=True)
    start: NamedPlace
    end: NamedPlace
    profile: TravelMethod = Field(
        TravelMethod.drive, description="Isochrone profile used in the calculation."
    )

    def __str__(self) -> str:
        words = ["ROUTE FROM", str(self.start), "TO", str(self.end)]
        return " ".join(words)


class OpenAIDerivedIntent(_LocalModel):
    intent: Any  # TODO how to get the intent class here?
    type: Literal["openai_derived_intent"] = Field("openai_derived_intent", const=True)
    args: Dict[str, Any]

    def __str__(self) -> str:
        return str(self.intent)

QueryIntent = Union[
    Route,
    Isochrone,
    OpenAIDerivedIntent,
    Buffer,
    SpRelCoveredBy,
    SpRelDisjoint,
    SpRelWithinDistOf,
    SpRelOutsideDistOf,
    SpRelNear,
    SpRelNotNear,
    SpRelWithinTimeOf,
    SpRelOutsideTimeOf,
    Place,
    NamedPlace,
]


class ParsedQuery(_LocalModel):
    """Parse of a query."""

    value: QueryIntent = Field(..., description="Query intent", discriminator="type")
    text: str
    tokens: List[str]

    def __str__(self) -> str:
        return str(self.value)
