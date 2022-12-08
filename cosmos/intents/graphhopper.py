import os

import requests

from app.core.config import get_settings

settings = get_settings()
api_key = settings.graphhopper.api_key

"""Return the isochrone for a given location and time."""
# Get the location and time from the request
def isochrone(
    lng: float, lat: float, s: int, vehicle: str = "car"
):
    # Get the isochrone for the given location and time
    url = f"https://graphhopper.com/api/1/isochrone?point={lat},{lng}&time_limit={s}&vehicle={vehicle}&" \
            f"key={api_key}"
    response = requests.get(url)
    return response.json()