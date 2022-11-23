# pylint: disable=too-few-public-methods
"""Custom Pydantic Data Types."""
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Literal, NamedTuple, Optional, Union

# pylint: disable=no-name-in-module
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConstrainedFloat, Field

# pylint: enable=no-name-in-module


class BaseModel(PydanticBaseModel):
    """Local BaseModel class to add common functionality."""


class AppEnvEnum(str, Enum):
    """Environment in which the app is being run."""

    PROD = "PROD"
    DEV = "DEV"
    TEST = "TEST"
    STAGING = "STAGING"

    def __str__(self) -> str:
        return str(self.value)


class LogLevel(str, Enum):
    """Python logging module log level constants represented as an ``enum.Enum``."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    def __str__(self) -> str:
        return str(self.value)


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


class MapProjection(int, Enum):
    """Map projection codes."""

    WGS84 = 4326
    WEB_MERCATOR = 3857


class Position(NamedTuple):
    """Latitude and longitude coordinates."""

    lng: Longitude
    lat: Latitude


PointCoord = Position
LineStringCoord = List[PointCoord]
MultiPointCoord = List[PointCoord]
PolygonCoord = List[LineStringCoord]
MultiLineStringCoord = List[LineStringCoord]
MultiPolygonCoord = List[PolygonCoord]


class BBox(NamedTuple):
    """Bounding box."""

    min_x: Longitude = Field(-180)
    min_y: Latitude = Field(-90)
    max_x: Longitude = Field(180)
    max_y: Latitude = Field(90)


class Point(BaseModel):
    """GeoJSON Point."""

    type: Literal["Point"] = Field("Point", const=True)
    coordinates: PointCoord = Field(...)


class MultiPoint(BaseModel):
    """GeoJSON MultiPoint."""

    type: Literal["MultiPoint"] = Field("MultiPoint", const=True)
    coordinates: MultiPointCoord = Field(...)


class LineString(BaseModel):
    """GeoJSON LineString."""

    type: Literal["LineString"] = Field("LineString", const=True)
    coordinates: LineStringCoord = Field(...)


class MultiLineString(BaseModel):
    """GeoJSON MultiLineString."""

    type: Literal["MultiLineString"] = Field("MultiLineString", const=True)
    coordinates: MultiLineStringCoord = Field(...)


class Polygon(BaseModel):
    """GeoJSON Polygon."""

    type: Literal["Polygon"] = Field("Polygon", const=True)
    coordinates: PolygonCoord = Field(...)


class MultiPolygon(BaseModel):
    """GeoJSON MultiPoint."""

    type: Literal["MultiPolygon"] = Field("MultiPolygon", const=True)
    coordinates: MultiPolygonCoord = Field(...)


Geometry = Union[Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon]


class Feature(BaseModel):
    """Feature class."""

    type: Literal["Feature"] = Field("Feature", const=True)
    id: Union[None, str, int] = Field(None)
    properties: Optional[Dict[str, Any]] = Field(None)
    geometry: Geometry = Field(..., discriminator="type")
    bbox: Optional[BBox] = Field(None)


class FeatureCollection(BaseModel):
    """GeoJSON FeatureCollection class."""

    type: Literal["FeatureCollection"] = Field("FeatureCollection", const=True)
    features: List[Feature] = Field(default_factory=list)
    bbox: Optional[BBox] = Field(None)
