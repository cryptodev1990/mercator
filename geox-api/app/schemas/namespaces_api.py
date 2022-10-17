"""Complex objects used as the output of APIs."""
from typing import List, Optional

from pydantic import Field

from .namespaces import Namespace
from .shape import GeoShapeMetadata


class NamespaceResponse(Namespace):
    """Response in get namespaces."""

    shapes: Optional[List[GeoShapeMetadata]] = Field(
        default_factory=list,
        description="""
        List of shape metadata of shapes in the namespace.
        None means that shape metadata wasn't requested.
        An empty list means that there are no shapes.""",
    )
