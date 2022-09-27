"""API Schema."""
import datetime
from typing import Any, List, Optional

from geojson_pydantic import Feature
from pydantic import UUID4, Field

from app.schemas.common import BaseModel

__all__ = []

class GeoShapeCreate(BaseModel):
    name: Optional[str] = Field(None, description="Name of the shape")
    geojson: Feature = Field(..., description="GeoJSON representation of the shape")

__all__.append("GeoShapeCreate")

class GeoShapeRead(BaseModel):
    uuid: UUID4 = Field(..., description="Unique identifier for the shape")

__all__.append("GeoShapeRead")

class GeoShapeUpdate(GeoShapeRead):
    name: Optional[str]
    geojson: Optional[Feature]
    should_delete: Optional[bool] = Field(
        False, description="If true, deletes the shape"
    )

__all__.append("GeoShapeUpdate")

class GeoShape(GeoShapeRead, GeoShapeCreate):
    created_by_user_id: int = Field(..., description="User ID of the creator")
    created_at: datetime.datetime = Field(..., description="Date and time of creation")
    updated_by_user_id: Optional[int] = Field(
        None, description="User ID of the most recent updater"
    )
    updated_at: Optional[datetime.datetime] = Field(
        None, description="Date and time of most recent updater"
    )

__all__.append("GeoShape")

class ShapeCountResponse(BaseModel):
    num_shapes: int = Field(..., description="Number of shapes affected by transaction")

__all__.append("ShapeCountResponse")

class BulkGeoShapeCreate(BaseModel):
    shapes: List[GeoShapeCreate] = Field(
        ..., description="List of GeoShapeCreate objects"
    )

__all__.append("BulkGeoShapeCreate")

class CeleryTaskResponse(BaseModel):
    """Response from submitting a Celery task."""

    task_id: str = Field(..., description="Task id.")

__all__.append("CeleryTaskResponse")


class CeleryTaskResult(BaseModel):
    """Result of a Celery task."""

    task_id: str = Field(..., description="Task id.")
    task_status: str = Field(..., description="Task status.")
    task_result: Any = Field(..., description="Task results.")

__all__.append("CeleryTaskResult")


class AppVersion(BaseModel):
    """Version information about the app."""

    version: str = Field(..., description="App version number.")
    git_commit: Optional[str] = Field(description="Git hash")

__all__.append("AppVersion")