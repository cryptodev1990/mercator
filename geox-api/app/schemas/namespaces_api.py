"""Complex objects used as the output of APIs."""
from .namespaces import Namespace
from .shape import GeoShapeMetadata
from pydantic import Field
from typing import Optional


from typing import List


class NamespaceResponse(Namespace):
    """Response in get namespaces."""

    shapes: Optional[List[GeoShapeMetadata]] = Field(
        default_factory=list,
        description="""
        List of shape metadata of shapes in the namespace.
        None means that shape metadata wasn't requested.
        An empty list means that there are no shapes.""",
    )
