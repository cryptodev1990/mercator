# openapi_client.MapMatchingAPIApi

All URIs are relative to *https://graphhopper.com/api/1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**post_gpx**](MapMatchingAPIApi.md#post_gpx) | **POST** /match | Map-match a GPX file


# **post_gpx**
> RouteResponse post_gpx()

Map-match a GPX file

### Example You get an example response for a GPX via:  ``` curl -XPOST -H \"Content-Type: application/gpx+xml\" \"https://graphhopper.com/api/1/match?profile=car&key=[YOUR_KEY]\" --data @/path/to/some.gpx ```  A minimal working GPX file looks like ```gpx <gpx>  <trk>   <trkseg>    <trkpt lat=\"51.343657\" lon=\"12.360708\"></trkpt>    <trkpt lat=\"51.343796\" lon=\"12.361337\"></trkpt>    <trkpt lat=\"51.342784\" lon=\"12.361882\"></trkpt>   </trkseg>  </trk> </gpx> ```  ### Introduction ![Map Matching screenshot](./img/map-matching-example.gif)  The Map Matching API is part of the GraphHopper Directions API and with this API you can snap measured GPS points typically as GPX files to a digital road network to e.g. clean data or attach certain data like elevation or turn instructions to it. Read more at Wikipedia.  In the example screenshot above and demo you see the Map Matching API in action where the black line is the GPS track and the green one is matched result.  To get a match response you send a GPX file in the body of an HTTP POST request and specify request parameters like the `key` and `profile` in the URL. See below for more supported parameters.  ### API Clients and Examples See the [clients](#section/API-Clients) section in the main documentation, and [live examples](https://graphhopper.com/api/1/examples/#map-matching).  ### Limits and Counts The cost for one request depends on the number of GPS location and is documented [here](https://graphhopper.com/api/1/docs/FAQ/).  One request should not exceed the Map Matching API location limit depending on the package, see the pricing in our dashboard. 

### Example

* Api Key Authentication (api_key):

```python
import time
import openapi_client
from openapi_client.api import map_matching_api_api
from openapi_client.model.route_response import RouteResponse
from openapi_client.model.gh_error import GHError
from pprint import pprint
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
configuration.api_key['api_key'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_key'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = map_matching_api_api.MapMatchingAPIApi(api_client)
    gps_accuracy = 1 # int | Specify the precision of a point, in meter (optional)
    profile = "car" # str |  (optional) if omitted the server will use the default value of "car"
    locale = "en" # str | The locale of the resulting turn instructions. E.g. `pt_PT` for Portuguese or `de` for German.  (optional) if omitted the server will use the default value of "en"
    elevation = False # bool | If `true`, a third coordinate, the altitude, is included with all positions in the response. This changes the format of the `points` and `snapped_waypoints` fields of the response, in both their encodings. Unless you switch off the `points_encoded` parameter, you need special code on the client side that can handle three-dimensional coordinates.  (optional) if omitted the server will use the default value of False
    details = [
        "details_example",
    ] # [str] | Optional parameter to retrieve path details. You can request additional details for the route: `street_name`,  `time`, `distance`, `max_speed`, `toll`, `road_class`, `road_class_link`, `road_access`, `road_environment`, `lanes`, and `surface`. Read more about the usage of path details [here](https://discuss.graphhopper.com/t/2539).  (optional)
    instructions = True # bool | If instructions should be calculated and returned  (optional) if omitted the server will use the default value of True
    calc_points = True # bool | If the points for the route should be calculated at all.  (optional) if omitted the server will use the default value of True
    points_encoded = True # bool | Allows changing the encoding of location data in the response. The default is polyline encoding, which is compact but requires special client code to unpack. (We provide it in our JavaScript client library!) Set this parameter to `false` to switch the encoding to simple coordinate pairs like `[lon,lat]`, or `[lon,lat,elevation]`. See the description of the response format for more information.  (optional) if omitted the server will use the default value of True

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Map-match a GPX file
        api_response = api_instance.post_gpx(gps_accuracy=gps_accuracy, profile=profile, locale=locale, elevation=elevation, details=details, instructions=instructions, calc_points=calc_points, points_encoded=points_encoded)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling MapMatchingAPIApi->post_gpx: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **gps_accuracy** | **int**| Specify the precision of a point, in meter | [optional]
 **profile** | **str**|  | [optional] if omitted the server will use the default value of "car"
 **locale** | **str**| The locale of the resulting turn instructions. E.g. &#x60;pt_PT&#x60; for Portuguese or &#x60;de&#x60; for German.  | [optional] if omitted the server will use the default value of "en"
 **elevation** | **bool**| If &#x60;true&#x60;, a third coordinate, the altitude, is included with all positions in the response. This changes the format of the &#x60;points&#x60; and &#x60;snapped_waypoints&#x60; fields of the response, in both their encodings. Unless you switch off the &#x60;points_encoded&#x60; parameter, you need special code on the client side that can handle three-dimensional coordinates.  | [optional] if omitted the server will use the default value of False
 **details** | **[str]**| Optional parameter to retrieve path details. You can request additional details for the route: &#x60;street_name&#x60;,  &#x60;time&#x60;, &#x60;distance&#x60;, &#x60;max_speed&#x60;, &#x60;toll&#x60;, &#x60;road_class&#x60;, &#x60;road_class_link&#x60;, &#x60;road_access&#x60;, &#x60;road_environment&#x60;, &#x60;lanes&#x60;, and &#x60;surface&#x60;. Read more about the usage of path details [here](https://discuss.graphhopper.com/t/2539).  | [optional]
 **instructions** | **bool**| If instructions should be calculated and returned  | [optional] if omitted the server will use the default value of True
 **calc_points** | **bool**| If the points for the route should be calculated at all.  | [optional] if omitted the server will use the default value of True
 **points_encoded** | **bool**| Allows changing the encoding of location data in the response. The default is polyline encoding, which is compact but requires special client code to unpack. (We provide it in our JavaScript client library!) Set this parameter to &#x60;false&#x60; to switch the encoding to simple coordinate pairs like &#x60;[lon,lat]&#x60;, or &#x60;[lon,lat,elevation]&#x60;. See the description of the response format for more information.  | [optional] if omitted the server will use the default value of True

### Return type

[**RouteResponse**](RouteResponse.md)

### Authorization

[api_key](../README.md#api_key)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Routing Result |  * X-RateLimit-Limit - Your current daily credit limit. <br>  * X-RateLimit-Remaining - Your remaining credits until the reset. <br>  * X-RateLimit-Reset - The number of seconds that you have to wait before a reset of the credit count is done. <br>  * X-RateLimit-Credits - The credit costs for this request. Note it could be a decimal and even negative number, e.g. when an async request failed. <br>  |
**0** | Unexpected Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

