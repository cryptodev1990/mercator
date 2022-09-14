"""API Routes."""
from . import health, info, organizations, osm, shapes, shapes_new, tasks  # noqa

__all__ = [
    "health",
    "shapes",
    "tasks",
    "osm",
    "info",
    "organizations",
    "shapes_new",
]  # noqa
