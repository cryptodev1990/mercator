"""Functions for graphhopper API.

See `<https://www.graphhopper.com/developers/>`__.
"""
from functools import lru_cache
from typing import Any, Dict, Optional, Tuple

import httpx
from httpx import Response

from app.core.config import get_settings
from app.core.datatypes import BBox, Latitude, Longitude


class GraphHopper:
    """Graphhopper API Client..

    This is not a general purpose client, but rather a thin wrapper around the
    functions that are needed for the app.

    See `<https://docs.graphhopper.com/>`__.

    """

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def _get(self, url: str, params: Dict[str, Any] = None) -> Response:
        params = params or {}
        params["key"] = self._api_key
        return httpx.get(url, params=params)

    def geocode(self, query: str, bbox: BBox = None, limit: int = 1) -> Dict[str, Any]:
        """Geocode a query using OSM Nomatim."""
        params: Dict[str, Any] = {
            "locale": "en-US",
            "limit": limit,
            "q": query,
            "provider": "nominatim",
            "key": self._api_key,
        }
        if bbox:
            params["bounds"] = ",".join([str(c) for c in bbox])
        url = "https://graphhopper.com/api/1/geocode"
        response = self._get(url, params=params)
        response.raise_for_status()
        return response.json()

    def isochrone(
        self,
        point: Tuple[Latitude, Longitude],
        time_limit: float,
        profile: str = "car",
        reverse_flow: bool = True,
    ) -> Dict[str, Any]:
        """Geocode a query using OSM Nomatim."""
        params: Dict[str, Any] = {
            "point": ",".join([str(c) for c in point]),
            "profile": profile,
            "time_limit": time_limit,
            # X within time of Y should use the reverse_flow
            "reverse_flow": reverse_flow,
        }
        url = "https://graphhopper.com/api/1/isochrone"
        response = self._get(url, params=params)
        response.raise_for_status()
        return response.json()


@lru_cache()
def get_graph_hopper() -> Optional[GraphHopper]:
    """Return a GraphHopper client."""
    settings = get_settings()
    if settings.graph_hopper.api_key:
        return GraphHopper(api_key=settings.graph_hopper.api_key.get_secret_value())
    return None
