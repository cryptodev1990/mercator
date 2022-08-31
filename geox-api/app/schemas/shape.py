"""API Schema."""
import datetime
from typing import Any, List, Optional

from geojson_pydantic import Feature
from pydantic import UUID4, BaseModel, Field


class GeoShapeCreate(BaseModel):
    name: Optional[str] = Field(None, description="Name of the shape")
    geojson: Feature = Field(..., description="GeoJSON representation of the shape")


class GeoShapeRead(BaseModel):
    uuid: UUID4 = Field(..., description="Unique identifier for the shape")


class GeoShapeUpdate(GeoShapeRead):
    name: Optional[str]
    geojson: Optional[Feature]
    should_delete: Optional[bool] = Field(
        False, description="If true, deletes the shape"
    )


class GeoShape(GeoShapeRead, GeoShapeCreate):
    created_by_user_id: int = Field(..., description="User ID of the creator")
    created_at: datetime.datetime = Field(..., description="Date and time of creation")
    updated_by_user_id: Optional[int] = Field(
        None, description="User ID of the most recent updater"
    )
    updated_at: Optional[datetime.datetime] = Field(
        None, description="Date and time of most recent updater"
    )

    class Config:
        orm_mode = True


class ShapeCountResponse(BaseModel):
    num_shapes: int = Field(..., description="Number of shapes affected by transaction")


class BulkGeoShapeCreate(BaseModel):
    shapes: List[GeoShapeCreate] = Field(
        ..., description="List of GeoShapeCreate objects"
    )


class CeleryTaskResponse(BaseModel):
    """Response from submitting a Celery task."""

    task_id: str = Field(..., description="Task id.")


class CeleryTaskResult(BaseModel):
    """Result of a Celery task."""

    task_id: str = Field(..., description="Task id.")
    task_status: str = Field(..., description="Task status.")
    task_result: Any = Field(..., description="Task results.")


class AppVersion(BaseModel):
    """Version information about the app."""

    version: str = Field(..., description="App version number.")
    git_commit: Optional[str] = Field(description="Git hash")
