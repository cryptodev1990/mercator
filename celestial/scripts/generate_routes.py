from math import radians, cos, sin, asin, sqrt

import os
import random
from threading import local
import time
import openapi_client
from openapi_client.api import routing_api_api

from dotenv import load_dotenv

load_dotenv()

# Defining the host is optional and defaults to https://graphhopper.com/api/1
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://graphhopper.com/api/1"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: api_key
configuration.api_key['api_key'] = os.environ['GRAPHHOPPER_API_KEY']


def generate_random_point():
    rand_lat = random.uniform(31.466153715024294, 42.35854391749705)
    rand_lng = random.uniform(-125.20019531250001, -111.62109375000001)
    return [rand_lng, rand_lat]


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 3956 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r


def get_route(lng0: float, lat0: float, lng1: float, lat1: float) -> dict:
    time.sleep(0.5)
    with openapi_client.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = routing_api_api.RoutingAPIApi(api_client)
        points = [
            f"{lat0},{lng0}",
            f"{lat1},{lng1}",
        ] # [str] | The points for which the route should be calculated. Format: `latitude,longitude`. Specify at least an origin and a destination. Via points are possible. The maximum number depends on your plan. 
        profile = "car" # str |  (optional) if omitted the server will use the default value of "car"
        # example passing only required values which don't have defaults set
        try:
            # GET Route Endpoint
            api_response = api_instance.get_route(points, profile=profile)
            return api_response
        except openapi_client.ApiException as e:
            print("Exception when calling RoutingAPIApi->get_route: %s\n" % e)
            return {}


def main():
    points = []
    while len(points) < 1000:
        p0, p1 = [], []
        route = None
        while not route:
            distance_between = -1
            while distance_between < 50:
                p0 = generate_random_point()
                p1 = generate_random_point()
                distance_between = haversine(*[*p0, *p1])
            try:
                route = get_route(p0[0], p0[1], p1[0], p1[1])
                route = route['paths'][0]['points']
            except:
                pass
        points.append(route)
        print(str(len(points)) + " points generated")
    with open("routes.txt", "w") as f:
        for point in points:
            f.write(str(point) + "\n")
    print('done')

if __name__ == '__main__':
    main()
