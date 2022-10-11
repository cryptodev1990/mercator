"""Complex objects used as the output of APIs."""
from .namespaces import Namespace
from .shape import GeoShapeMetadata
from pydantic import Field


from typing import List


class NamespaceResponse(Namespace):
    """Response in get namespaces."""

    shapes: List[GeoShapeMetadata] = Field(
        [], description="List of shape metadata of shapes in the namespace"
    )

