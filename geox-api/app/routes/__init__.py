"""API Routes."""
from . import health, info, osm, shapes, shapes_new, tasks  # noqa

__all__ = [
    "health",
    "shapes",
    "tasks",
    "osm",
    "info",
    "shapes_new",
]  # noqa
