"""API Routes."""
from . import health, info, organizations, osm, shapes, tasks  # noqa

__all__ = [
    "health",
    "shapes",
    "tasks",
    "osm",
    "info",
    "organizations",
]  # noqa
