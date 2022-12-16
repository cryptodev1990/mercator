import random
import time

import aiohttp
import asyncio

from typing import List, Union

import requests

# from app.core.config import get_settings

GH_BASE = "https://graphhopper-1.fly.dev"

# Generate a route from the Graphhopper API
def route(
    lng: float,
    lat: float,
    lng2: float,
    lat2: float,
    vehicle: str = "car",
    elevation: bool = False,
):
    # Get the route for the given location and time
    url = f"{GH_BASE}/route?point={lat},{lng}&point={lat2},{lng2}&vehicle={vehicle}&elevation={elevation}"
    response = requests.get(url)
    return response.json()


def get_route(
    session: aiohttp.ClientSession, route: List[Union[float, int]]
):
    """Get the route for a given location and time."""
    vehicle = "car"
    lng, lat, lng2, lat2 = route
    url = f"{GH_BASE}/route?point={lat},{lng}&point={lat2},{lng2}&vehicle={vehicle}&elevation=false&instructions=false"
    res = session.get(url)
    return res


async def multiple_concurrent_routes(
    route_list: List[List]
):
    """Get multiple routes concurrently."""

    async with aiohttp.ClientSession() as session:
        tasks = []
        for route in route_list:
            tasks.append(asyncio.create_task(get_route(session, route)))
        fan_in = await asyncio.gather(*tasks)

        results = []
        for response in fan_in:
            results.append(await response.json())
        return results


def decode_polyline(polyline_str):
    index, lat, lng = 0, 0, 0
    coordinates = []
    changes = {'latitude': 0, 'longitude': 0}

    # Coordinates have variable length when encoded, so just keep
    # track of whether we've hit the end of the string. In each
    # while loop iteration, a single coordinate is decoded.
    while index < len(polyline_str):
        # Gather lat/lon changes, store them in a dictionary to apply them later
        for unit in ['latitude', 'longitude']: 
            shift, result = 0, 0

            while True:
                byte = ord(polyline_str[index]) - 63
                index+=1
                result |= (byte & 0x1f) << shift
                shift += 5
                if not byte >= 0x20:
                    break

            if (result & 1):
                changes[unit] = ~(result >> 1)
            else:
                changes[unit] = (result >> 1)

        lat += changes['latitude']
        lng += changes['longitude']

        coordinates.append((lat / 100000.0, lng / 100000.0))

    return coordinates


if __name__ == "__main__":
    # Generate 100000 random routes within a bounding box of northern california
    # We're not guaranteed to get a route for each of these
    # Get the bounding box for northern CA
    BBOX = [-124.848974, 32.528832, -114.131211, 42.009518]
    route_list = []
    for i in range(100):
        lng = random.uniform(BBOX[0], BBOX[2])
        lat = random.uniform(BBOX[1], BBOX[3])
        lng2 = random.uniform(BBOX[0], BBOX[2])
        lat2 = random.uniform(BBOX[1], BBOX[3])
        route_list.append([lng, lat, lng2, lat2, False])
    start = time.time()
    start = time.time()
    asyncio.run(multiple_concurrent_routes(route_list))