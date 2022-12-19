"""FastAPI response schemes."""
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import UUID4, BaseModel, Field  # pylint: disable=no-name-in-module

from app.core.datatypes import Feature, FeatureCollection


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
