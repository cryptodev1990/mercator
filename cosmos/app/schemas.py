"""FastAPI response schemes."""
from enum import Enum
import json
from re import L

from typing import Any, Dict, List, Optional, Union

from pydantic import UUID4, BaseModel, Field
from typer import Option  # pylint: disable=no-name-in-module

from app.core.datatypes import Feature, FeatureCollection


from enum import auto
from fastapi_utils.enums import StrEnum


class ValidIntentNameEnum(StrEnum):
    """Argument for valid_intent constraint."""

    x_in_y = auto()
    area_near_constraint = auto()
    raw_lookup = auto()
    x_between_y_and_z = auto()



class Schema(BaseModel):
    """Base schema class."""


class HealthStatus(str, Enum):
    """Helath status codes."""

    OK = "OK"
    ERROR = "ERROR"


class HealthResponse(BaseModel):
    """Health response model."""

    message: HealthStatus


OsmQueryParse = Dict[str, Any]
"""Represents information about the parsed query.

The format of this dictionary is subject to change.
"""

class ParsedEntity(BaseModel):
    lookup: str = Field(..., description="The original lookup string.")
    matched_text: Optional[str] = None
    match_type: str = Field(..., description="Can either be 'named_place' or 'category' or 'fuzzy'.")
    geoids: Optional[List[str]] = None
    # Add an optional distance_in_meters field
    m: Optional[float] = None


class NamedPlaceParsedEntity(ParsedEntity):
    """A parsed entity that represents a named place."""

    match_type = "named_place"

    def __init__(self, lookup: str, geoids: Optional[List[str]] = None, **kwargs: Any) -> None:
        super().__init__(lookup=lookup, geoids=geoids, **kwargs)


class LatLng(BaseModel):
    """A latitude/longitude pair."""

    lat: float = Field(..., description="Latitude.")
    lng: float = Field(..., description="Longitude.")


class EnrichedEntity(ParsedEntity):
    """An entity with additional information"""
    lookup: str
    # Can either be "named_place" or "known_category"
    match_type: str
    geoids: List[str]
    sql_snippet: str
    pt: Optional[LatLng] = None

    def __str__(self):
        return json.dumps({
            "lookup": self.lookup,
            "match_type": self.match_type,
            "geoids": self.geoids,
        })

    # the following function overrides the Pydantic .json() method
    # to return the string representation of the object
    def json(self, *args, **kwargs):
        return json.dumps({
            "lookup": self.lookup,
            "match_type": self.match_type,
            "geoids": self.geoids,
        })

    def __repr__(self):
        return self.__str__()


class ExecutorResponse(BaseModel):
    """Response for executor."""

    geom: FeatureCollection
    entities: List[ParsedEntity]

    class Config:
        """Pydantic config options."""

class OsmSearchResponse(BaseModel):
    """Response for OSM search."""

    query: str = Field(..., description="The query string from the request.")
    label: Optional[str] = Field(
        None, description="A label that can be used to identify the query."
    )
    parse: Optional[OsmQueryParse] = Field(
        None,
        description=(
            "Details about how the query was parsed."
            "The format of this field is subject to change."
        ),
    )
    results: FeatureCollection = Field(
        ..., description="Feature collection of spatial features matching the query."
    )
    id: UUID4 = Field(..., description="Unique ID for this query.")

    class Config:
        """Pydantic config."""

        # pylint: disable=line-too-long
        schema_extra = {
            "example": {
                "query": "Coffee shops in San Francisco",
                "label": "Coffee shops IN San Francisco",
                "parse": {
                    "value": {
                        "subject": {
                            "type": "place",
                            "value": ["Coffee", "shops"],
                        },
                        "object": {"type": "named_place", "value": ["San Francisco"]},
                        "type": "covered_by",
                    },
                    "text": "Coffee shops in San Francisco",
                    "tokens": ["Coffee", "shops", "in", "San Francisco"],
                },
                "results": {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "id": "960932055",
                            "properties": {
                                "osm": {
                                    "id": 960932055,
                                    "tags": {
                                        "name": "Java Beach Cafe",
                                        "phone": "+1-415-665-5282",
                                        "amenity": "cafe",
                                        "cuisine": "coffee_shop",
                                        "website": "http://www.javabeachsf.com",
                                        "addr:street": "La Playa Street",
                                        "addr:postcode": "94122",
                                        "opening_hours": "Mo-Su 06:30-17:00",
                                        "outdoor_seating": "yes",
                                        "addr:housenumber": "1396",
                                    },
                                    "type": "N",
                                    "category": "point",
                                }
                            },
                            "geometry": {"type": "Point", "coordinates": [-122.508978, 37.7604494]},
                            "bbox": [-122.508978, 37.7604494, -122.508978, 37.7604494],
                        }
                    ],
                    "bbox": [-122.508978, 37.7604494, -122.508978, 37.7604494],
                },
                "id": "6f8b6f8b-6f8b-6f8b-6f8b-6f8b6f8b6f8b",
            }
        }

    # pylint: enable=line-too-long


class OsmShapeForIdResponse(BaseModel):
    """Response for querying OSM for given OSM ID."""

    osm_id: int = Field(..., description="The OSM ID from the request.")
    result: Feature = Field(
        ..., description="Feature of matching the query. Note that search API returns List[Feature]."
    )
    class Config:
        """Pydantic config."""


class OsmRawQueryResponse(BaseModel):
    """Response for raw SQL executed against OSM."""

    query: str
    results: List[Dict[str, Any]]

    class Config:
        """Pydantic config options."""


class XInYIntentArgs(BaseModel):
    """Arguments for x_in_y constraint."""

    needle_place_or_amenity: ParsedEntity | str = Field(
        ..., description="Place or amenity to search for."
    )
    haystack_place_or_amenity: ParsedEntity | str = Field(
        ..., description="Place or amenity to search in."
    )

    class Config:
        """Pydantic config options."""

        schema_extra = {
            "example": {
                "needle_place_or_amenity": {
                    "lookup": "coffee shops",
                    "match_type": "fuzzy",
                },
                "haystack_place_or_amenity": {
                    "lookup": "San Francisco",
                    "match_type": "named_place",
                },
            }
        }


class AreaNearConstraintIntentArgs(BaseModel):
    """Arguments for area_near_constraint constraint."""

    named_place_or_amenity_0: ParsedEntity | str = Field(
        ..., description="Place or amenity to search for."
    )
    distance_or_time_0: ParsedEntity | str = Field(
        ..., description="Distance or time to search for."
    )
    named_place_or_amenity_1: ParsedEntity | str = Field(
        ..., description="Place or amenity to search for."
    )
    distance_or_time_1: ParsedEntity | str = Field(
        ..., description="Distance or time to search for."
    )
    # TODO is there a more elegant way to do this?
    named_place_or_amenity_2: Optional[ParsedEntity | str] = None
    distance_or_time_2: Optional[str | float] = None
    named_place_or_amenity_3: Optional[ParsedEntity | str] = None
    distance_or_time_3: Optional[str | float] = None
    named_place_or_amenity_4: Optional[ParsedEntity | str] = None
    distance_or_time_4: Optional[str | float] = None
    named_place_or_amenity_5: Optional[ParsedEntity | str] = None
    distance_or_time_5: Optional[str | float] = None
    named_place_or_amenity_6: Optional[ParsedEntity | str] = None
    distance_or_time_6: Optional[str | float] = None
    named_place_or_amenity_7: Optional[ParsedEntity | str] = None
    distance_or_time_7: Optional[str | float] = None


    class Config:
        """Pydantic config options."""

        schema_extra = {
            "example": {
                "name": "area_near_constraint",
                "args": {
                    "named_place_or_amenity_0": {
                        "lookup": "coffee shops",
                        "match_type": "fuzzy",
                    },
                    "distance_or_time_0": "1 mile",
                    "named_place_or_amenity_1": {
                        "lookup": "grocery stores",
                        "match_type": "fuzzy",
                    },
                    "distance_or_time_1": "1 mile",
                }
            }
        }

class RawLookupIntentArgs(BaseModel):
    """Arguments for raw_lookup constraint."""

    raw_lookup: Union[str, ParsedEntity] = Field(
        ..., description="Raw lookup to search for."
    )

    class Config:
        """Pydantic config options."""

        schema_extra = {
            "example": {
                "raw_lookup": "coffee shops",
            }
        }


class XBetweenYAndZIntentArgs(BaseModel):
    """Arguments for x_between_y_and_z constraint."""

    named_place_or_amenity_0: ParsedEntity | str = Field(..., description="X to search for.")
    named_place_or_amenity_1: NamedPlaceParsedEntity | str = Field(..., description="Y to search for.")
    named_place_or_amenity_2: NamedPlaceParsedEntity | str = Field(..., description="Z to search for.")

    class Config:
        """Pydantic config options."""

        schema_extra = {
            "example": {
                "named_place_or_amenity_0": {
                    "lookup": "coffee shops",
                    "match_type": "fuzzy",
                },
                "named_place_or_amenity_1": {
                    "lookup": "San Francisco",
                    "match_type": "named_place",
                },
                "named_place_or_amenity_2": {
                    "lookup": "San Jose",
                    "match_type": "named_place",
                },
            }
        }


ValidIntentArgs = XInYIntentArgs | AreaNearConstraintIntentArgs | RawLookupIntentArgs | XBetweenYAndZIntentArgs

class IntentPayload(BaseModel):
    """Intent for a query."""

    name: ValidIntentNameEnum
    args: ValidIntentArgs

    class Config:
        """Pydantic config options."""

        schema_extra = {
            "example": {
                "name": "x_in_y",
                "args": {
                    "needle_place_or_amenity": {
                        "lookup": "coffee shops",
                        "match_type": "fuzzy",
                    },
                    "haystack_place_or_amenity": {
                        "lookup": "San Francisco",
                        "match_type": "named_place",
                    },
                },
            }
        }

class IntentResponse(BaseModel):

    id: UUID4 = Field(..., description="Unique ID for this query.")
    parse_result: ExecutorResponse = Field(..., description="The result of the query.")
    query: str = Field(..., description="The query string from the request.")
    intents: List[ValidIntentNameEnum] = Field(..., description="List of intents")
    slots: ValidIntentArgs = Field(..., description="List of slots")

