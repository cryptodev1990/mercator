"""API Schema."""
import datetime
from typing import Any, Dict, List, Optional, Sequence, Union

from geojson_pydantic import Feature, GeometryCollection
from geojson_pydantic.geometries import Geometry
from pydantic import UUID4, Field, root_validator  # pylint: disable=no-name-in-module

from app.core.datatypes import Latitude, Longitude
from app.schemas.common import BaseModel

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
    namespace_id: Optional[UUID4] = None
    properties: Dict[str, Any] = Field(
        default_factory=dict, description="Properties of the shape"
    )
    created_at: Optional[datetime.datetime] = Field(
        None, description="Date and time of creation"
    )
    updated_at: Optional[datetime.datetime] = Field(
        None, description="Date and time of most recent updater"
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


class GeoShape(BaseModel):
    uuid: UUID4
    geojson: Feature
    namespace_id: UUID4
    created_at: Optional[datetime.datetime] = Field(
        None, description="Date and time of creation"
    )
    updated_at: Optional[datetime.datetime] = Field(
        None, description="Date and time of most recent updater"
    )

    class Config:
        example = GeoShapeMetadata.Config.schema_extra["example"]
        example["geojson"] = EXAMPLE_GEOJSON


class GeoShapeCreate(BaseModel):
    name: Optional[str] = Field(None, description="Name of the shape")
    geojson: Optional[Feature] = Field(
        None, description="GeoJSON representation of the shape"
    )
    namespace: Optional[UUID4] = Field(None, description="Namespace id.")
    geometry: Union[None, Geometry, GeometryCollection] = Field(
        None, description="New shape"
    )
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)

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
    geometry: Union[None, Geometry, GeometryCollection] = None

    class Config:
        schema_extra = {
            "example": {
                "properties": {"New property": 10},
                "namespace_id": "cf9f83cd-d454-4abb-b77c-c6d639804618",
            }
        }


class ShapesDeletedResponse(BaseModel):
    deleted_ids: List[UUID4] = Field(default_factory=list)


class ShapeCountResponse(BaseModel):
    num_shapes: int = Field(..., description="Number of shapes affected by transaction")

    class Config:
        schema_extra = {"example": {"num_shapes": 5}}


class CeleryTaskResponse(BaseModel):
    """Response from submitting a Celery task."""

    task_id: str = Field(..., description="Task id.")


class ViewportBounds(BaseModel):
    min_x: Longitude = Field(..., description="Minimum X coordinate")
    min_y: Latitude = Field(..., description="Minimum Y coordinate")
    max_x: Longitude = Field(..., description="Maximum X coordinate")
    max_y: Latitude = Field(..., description="Maximum Y coordinate")

    # validate that the minimums are less than the maximums
    # pylint: disable=no-self-argument
    @root_validator()
    def validate_min_max(cls, value: Any) -> Any:
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
