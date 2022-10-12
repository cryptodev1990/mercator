"""API Schema."""
import datetime
from typing import Any, Dict, List, Optional, Union

from geojson_pydantic import Feature
from pydantic import UUID4, Field, root_validator

from app.schemas.common import BaseModel

# This is imported by __init__ with *
# Append all objects to exported in __all__

EXAMPLE_GEOJSON = {
    "type": "Feature",
    "properties": {},
    "geometry": {
        "type": "Polygon",
        "coordinates": [
            [
                [-122.26907730102539, 37.796084948503236],
                [-122.24555969238281, 37.796084948503236],
                [-122.24555969238281, 37.81208947621168],
                [-122.26907730102539, 37.81208947621168],
                [-122.26907730102539, 37.796084948503236],
            ]
        ],
    },
}
"""Example geojson feature to use in API docs.

It is a bounding box of Lake Merritt, Oakland, CA."""


class GeoShapeMetadata(BaseModel):
    """Metadata about a shape."""

    uuid: UUID4
    # Names are allowed to be null
    name: Optional[str] = Field(None, description="Name of the shape")
    # TODO: change to not-optional after UUID4 is done
    namespace_id: Optional[UUID4] = None
    properties: Dict[str, Any] = Field(..., description="Properties of the shape")
    created_at: datetime.datetime = Field(..., description="Date and time of creation")
    updated_at: Optional[datetime.datetime] = Field(
        ..., description="Date and time of most recent updater"
    )

    class Config:
        schema_extra = {
            "example": {
                "uuid": "9be2a343-60f5-4324-a5f4-4efe8efeba28",
                "name": "Lake Merritt",
                "properties": {},
                "namespace_id": "cf9f83cd-d454-4abb-b77c-c6d639804618",
            }
        }


class GeoShape(GeoShapeMetadata):
    geojson: Feature

    class Config:
        example = GeoShapeMetadata.Config.schema_extra["example"]
        example["geojson"] = EXAMPLE_GEOJSON


class GeoShapeCreate(BaseModel):
    name: Optional[str] = Field(None, description="Name of the shape")
    geojson: Feature = Field(..., description="GeoJSON representation of the shape")
    namespace: Optional[UUID4] = Field(None, description="Namespace id.")

    class Config:
        schema_extra = {
            "example": {
                "name": "Lake Merritt",
                "properties": {},
                "namespace_id": "cf9f83cd-d454-4abb-b77c-c6d639804618",
                "geojson": EXAMPLE_GEOJSON,
            }
        }


class GeoShapeUpdate(BaseModel):
    uuid: Optional[UUID4]  # TODO: this should be removed!
    name: Optional[str] = None
    geojson: Optional[Feature] = None
    properties: Optional[Dict[str, Any]] = None
    namespace: Optional[UUID4] = Field(None, description="The namespace id")

    # TODO: delete this - this should not be used at all
    should_delete: bool = Field(False, description="")

    class Config:
        schema_extra = {
            "example": {
                "properties": {"New property": 10},
                "namespace_id": "cf9f83cd-d454-4abb-b77c-c6d639804618",
            }
        }


class ShapeCountResponse(BaseModel):
    num_shapes: int = Field(..., description="Number of shapes affected by transaction")

    class Config:
        schema_extra = {"example": {"num_shapes": 5}}


class CeleryTaskResponse(BaseModel):
    """Response from submitting a Celery task."""

    task_id: str = Field(..., description="Task id.")


class ViewportBounds(BaseModel):
    min_x: float = Field(..., description="Minimum X coordinate")
    min_y: float = Field(..., description="Minimum Y coordinate")
    max_x: float = Field(..., description="Maximum X coordinate")
    max_y: float = Field(..., description="Maximum Y coordinate")

    # validate that the x values are valid geospatial coordinates
    @classmethod
    def validate(cls, value: Any) -> Any:
        if not (-180 <= value["min_x"] <= 180):
            raise ValueError("min_x must be between -180 and 180")
        if not (-180 <= value["max_x"] <= 180):
            raise ValueError("max_x must be between -180 and 180")
        if not (-90 <= value["min_y"] <= 90):
            raise ValueError("min_y must be between -90 and 90")
        if not (-90 <= value["max_y"] <= 90):
            raise ValueError("max_y must be between -90 and 90")
        return value

    # validate that the minimums are less than the maximums
    @classmethod
    def validate_min_max(cls, value: Any) -> Any:
        if value["min_x"] > value["max_x"]:
            raise ValueError("min_x must be less than max_x")
        if value["min_y"] > value["max_y"]:
            raise ValueError("min_y must be less than max_y")
        return value

    class Config:
        schema_extra = {
            "example": {
                "min_x": -122.245,
                "min_y": 37.8,
                "max_x": -122.27,
                "max_y": 37.81,
            }
        }


class CeleryTaskResult(BaseModel):
    """Result of a Celery task."""

    task_id: str = Field(..., description="Task id.")
    task_status: str = Field(..., description="Task status.")
    task_result: Any = Field(..., description="Task results.")


class AppVersion(BaseModel):
    """Version information about the app."""

    version: str = Field(..., description="App version number.")
    git_commit: Optional[str] = Field(description="Git hash")
