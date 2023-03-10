import json
import time

import aiohttp
import asyncio

from typing import List, Union

import requests

# from app.core.config import get_settings

GH_BASE = "https://graphhopper-1.fly.dev"


"""Return the isochrone for a given location and time."""
# Get the location and time from the request
def isochrone(
    lng: float, lat: float, s: int, vehicle: str = "car", buckets: int = 1
):
    # Get the isochrone for the given location and time
    url = f"{GH_BASE}/isochrone?point={lat},{lng}&time_limit={s}&vehicle={vehicle}&buckets={buckets}"
    response = requests.get(url)
    return response.json()


def get_iso(
    session: aiohttp.ClientSession, iso: List[Union[float, int, str]]
):
    """Get the isochrone for a given location and time."""
    vehicle = "car"
    lng, lat, s, buckets = iso
    url = f"{GH_BASE}/isochrone?point={lat},{lng}&time_limit={s}&vehicle={vehicle}&buckets={buckets}"
    res = session.get(url)
    return res


async def multiple_concurrent_iso(
    iso_list: List[List]
):
    """Get multiple isochrones concurrently."""

    async with aiohttp.ClientSession() as session:
        tasks = []
        for iso in iso_list:
            tasks.append(asyncio.create_task(get_iso(session, iso)))
        fan_in = await asyncio.gather(*tasks)

        results = []
        for response in fan_in:
            results.append(await response.json())
        return results


if __name__ == "__main__":
    # Get the isochrone for a given location and time
    # Get multiple isochrones concurrently
    iso_list = [
        [-122.47361205, 37.7515662, 1800, 1],
        [-122.47308425, 37.7515896, 1800, 1],
        [-122.4772409501, 37.74953675004, 1800, 1],
        [-122.4767617501, 37.7487522, 1800, 1],
        [-122.4767617, 37.7486217, 1800, 1],
        [-122.4767574501, 37.74856805, 1800, 1],
        [-122.4764282, 37.74831064999999, 1800, 1],
        [-122.47632315, 37.74831475, 1800, 1],
        [-122.47619384, 37.74810155, 1800, 1],
        [-122.47606945, 37.7479597, 1800, 1],
        [-122.47555025, 37.74840075, 1800, 1],
        [-122.47550964, 37.7486753, 1800, 1],
        [-122.47557714, 37.74880355005, 1800, 1],
        [-122.47535339, 37.7494159, 1800, 1],
        [-122.47486745, 37.7502423, 1800, 1],
        [-122.4745944, 37.75025435006, 1800, 1],
        [-122.47434565, 37.75060055, 1800, 1],
        [-122.47414885, 37.7515425, 1800, 1],
        [-122.47361205, 37.7515662, 1800, 1],
        [-122.47308425, 37.7515896, 1800, 1],
    ]
    loop = asyncio.get_event_loop()
    s = time.time()
    results = loop.run_until_complete(multiple_concurrent_iso(iso_list))
    print(json.dumps(results[0]['polygons'][0]).replace('0000', ''))
    print(time.time() - s)