# openapi_client.RoutingAPIApi

All URIs are relative to *https://graphhopper.com/api/1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_route**](RoutingAPIApi.md#get_route) | **GET** /route | GET Route Endpoint
[**post_route**](RoutingAPIApi.md#post_route) | **POST** /route | POST Route Endpoint
[**route_info_get**](RoutingAPIApi.md#route_info_get) | **GET** /route/info | Coverage information


# **get_route**
> RouteResponse get_route(point)

GET Route Endpoint

The GET request is the most simple one: just specify the parameter in the URL and you are done. Can be tried directly in every browser. 

### Example

* Api Key Authentication (api_key):

```python
import time
import openapi_client
from openapi_client.api import routing_api_api
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
    api_instance = routing_api_api.RoutingAPIApi(api_client)
    point = [
        "point_example",
    ] # [str] | The points for which the route should be calculated. Format: `latitude,longitude`. Specify at least an origin and a destination. Via points are possible. The maximum number depends on your plan. 
    profile = "car" # str |  (optional) if omitted the server will use the default value of "car"
    point_hint = [
        "point_hint_example",
    ] # [str] | The `point_hint` is typically a road name to which the associated `point` parameter should be snapped to. Specify no `point_hint` parameter or the same number as you have `point` parameters.  (optional)
    snap_prevention = [
        "snap_prevention_example",
    ] # [str] | Optional parameter to avoid snapping to a certain road class or road environment. Currently supported values are `motorway`, `trunk`, `ferry`, `tunnel`, `bridge` and `ford`. Multiple values are specified like `snap_prevention=ferry&snap_prevention=motorway`. Please note that in order to e.g. avoid motorways for the route (not for the \"location snap\") you need a different feature: a custom model.  (optional)
    curbside = [
        "any",
    ] # [str] | Optional parameter. It specifies on which side a point should be relative to the driver when she leaves/arrives at a start/target/via point. You need to specify this parameter for either none or all points. Only supported for motor vehicles and OpenStreetMap.  (optional)
    locale = "en" # str | The locale of the resulting turn instructions. E.g. `pt_PT` for Portuguese or `de` for German.  (optional) if omitted the server will use the default value of "en"
    elevation = False # bool | If `true`, a third coordinate, the altitude, is included with all positions in the response. This changes the format of the `points` and `snapped_waypoints` fields of the response, in both their encodings. Unless you switch off the `points_encoded` parameter, you need special code on the client side that can handle three-dimensional coordinates.  (optional) if omitted the server will use the default value of False
    details = [
        "details_example",
    ] # [str] | Optional parameter to retrieve path details. You can request additional details for the route: `street_name`,  `time`, `distance`, `max_speed`, `toll`, `road_class`, `road_class_link`, `road_access`, `road_environment`, `lanes`, and `surface`. Read more about the usage of path details [here](https://discuss.graphhopper.com/t/2539).  (optional)
    optimize = "false" # str | Normally, the calculated route will visit the points in the order you specified them. If you have more than two points, you can set this parameter to `\"true\"` and the points may be re-ordered to minimize the total travel time. Keep in mind that the limits on the number of locations of the Route Optimization API applies, and the request costs more credits.  (optional) if omitted the server will use the default value of "false"
    instructions = True # bool | If instructions should be calculated and returned  (optional) if omitted the server will use the default value of True
    calc_points = True # bool | If the points for the route should be calculated at all.  (optional) if omitted the server will use the default value of True
    debug = False # bool | If `true`, the output will be formatted.  (optional) if omitted the server will use the default value of False
    points_encoded = True # bool | Allows changing the encoding of location data in the response. The default is polyline encoding, which is compact but requires special client code to unpack. (We provide it in our JavaScript client library!) Set this parameter to `false` to switch the encoding to simple coordinate pairs like `[lon,lat]`, or `[lon,lat,elevation]`. See the description of the response format for more information.  (optional) if omitted the server will use the default value of True
    ch_disable = False # bool | Use this parameter in combination with one or more parameters from below.  (optional) if omitted the server will use the default value of False
    heading = [
        1,
    ] # [int] | Favour a heading direction for a certain point. Specify either one heading for the start point or as many as there are points. In this case headings are associated by their order to the specific points. Headings are given as north based clockwise angle between 0 and 360 degree. This parameter also influences the tour generated with `algorithm=round_trip` and forces the initial direction.  Requires `ch.disable=true`.  (optional)
    heading_penalty = 120 # int | Time penalty in seconds for not obeying a specified heading. Requires `ch.disable=true`.  (optional) if omitted the server will use the default value of 120
    pass_through = False # bool | If `true`, u-turns are avoided at via-points with regard to the `heading_penalty`. Requires `ch.disable=true`.  (optional) if omitted the server will use the default value of False
    algorithm = "round_trip" # str | Rather than looking for the shortest or fastest path, this parameter lets you solve two different problems related to routing: With `alternative_route`, we give you not one but several routes that are close to optimal, but not too similar to each other.  With `round_trip`, the route will get you back to where you started. This is meant for fun (think of a bike trip), so we will add some randomness. The `round_trip` option requires `ch.disable=true`. You can control both of these features with additional parameters, see below.   (optional)
    round_trip_distance = 10000 # int | If `algorithm=round_trip`, this parameter configures approximative length of the resulting round trip. Requires `ch.disable=true`.  (optional) if omitted the server will use the default value of 10000
    round_trip_seed = 1 # int | If `algorithm=round_trip`, this sets the random seed. Change this to get a different tour for each value.  (optional)
    alternative_route_max_paths = 2 # int | If `algorithm=alternative_route`, this parameter sets the number of maximum paths which should be calculated. Increasing can lead to worse alternatives.  (optional) if omitted the server will use the default value of 2
    alternative_route_max_weight_factor = 1.4 # float | If `algorithm=alternative_route`, this parameter sets the factor by which the alternatives routes can be longer than the optimal route. Increasing can lead to worse alternatives.  (optional) if omitted the server will use the default value of 1.4
    alternative_route_max_share_factor = 0.6 # float | If `algorithm=alternative_route`, this parameter specifies how similar an alternative route can be to the optimal route. Increasing can lead to worse alternatives.  (optional) if omitted the server will use the default value of 0.6

    # example passing only required values which don't have defaults set
    try:
        # GET Route Endpoint
        api_response = api_instance.get_route(point)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling RoutingAPIApi->get_route: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # GET Route Endpoint
        api_response = api_instance.get_route(point, profile=profile, point_hint=point_hint, snap_prevention=snap_prevention, curbside=curbside, locale=locale, elevation=elevation, details=details, optimize=optimize, instructions=instructions, calc_points=calc_points, debug=debug, points_encoded=points_encoded, ch_disable=ch_disable, heading=heading, heading_penalty=heading_penalty, pass_through=pass_through, algorithm=algorithm, round_trip_distance=round_trip_distance, round_trip_seed=round_trip_seed, alternative_route_max_paths=alternative_route_max_paths, alternative_route_max_weight_factor=alternative_route_max_weight_factor, alternative_route_max_share_factor=alternative_route_max_share_factor)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling RoutingAPIApi->get_route: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **point** | **[str]**| The points for which the route should be calculated. Format: &#x60;latitude,longitude&#x60;. Specify at least an origin and a destination. Via points are possible. The maximum number depends on your plan.  |
 **profile** | **str**|  | [optional] if omitted the server will use the default value of "car"
 **point_hint** | **[str]**| The &#x60;point_hint&#x60; is typically a road name to which the associated &#x60;point&#x60; parameter should be snapped to. Specify no &#x60;point_hint&#x60; parameter or the same number as you have &#x60;point&#x60; parameters.  | [optional]
 **snap_prevention** | **[str]**| Optional parameter to avoid snapping to a certain road class or road environment. Currently supported values are &#x60;motorway&#x60;, &#x60;trunk&#x60;, &#x60;ferry&#x60;, &#x60;tunnel&#x60;, &#x60;bridge&#x60; and &#x60;ford&#x60;. Multiple values are specified like &#x60;snap_prevention&#x3D;ferry&amp;snap_prevention&#x3D;motorway&#x60;. Please note that in order to e.g. avoid motorways for the route (not for the \&quot;location snap\&quot;) you need a different feature: a custom model.  | [optional]
 **curbside** | **[str]**| Optional parameter. It specifies on which side a point should be relative to the driver when she leaves/arrives at a start/target/via point. You need to specify this parameter for either none or all points. Only supported for motor vehicles and OpenStreetMap.  | [optional]
 **locale** | **str**| The locale of the resulting turn instructions. E.g. &#x60;pt_PT&#x60; for Portuguese or &#x60;de&#x60; for German.  | [optional] if omitted the server will use the default value of "en"
 **elevation** | **bool**| If &#x60;true&#x60;, a third coordinate, the altitude, is included with all positions in the response. This changes the format of the &#x60;points&#x60; and &#x60;snapped_waypoints&#x60; fields of the response, in both their encodings. Unless you switch off the &#x60;points_encoded&#x60; parameter, you need special code on the client side that can handle three-dimensional coordinates.  | [optional] if omitted the server will use the default value of False
 **details** | **[str]**| Optional parameter to retrieve path details. You can request additional details for the route: &#x60;street_name&#x60;,  &#x60;time&#x60;, &#x60;distance&#x60;, &#x60;max_speed&#x60;, &#x60;toll&#x60;, &#x60;road_class&#x60;, &#x60;road_class_link&#x60;, &#x60;road_access&#x60;, &#x60;road_environment&#x60;, &#x60;lanes&#x60;, and &#x60;surface&#x60;. Read more about the usage of path details [here](https://discuss.graphhopper.com/t/2539).  | [optional]
 **optimize** | **str**| Normally, the calculated route will visit the points in the order you specified them. If you have more than two points, you can set this parameter to &#x60;\&quot;true\&quot;&#x60; and the points may be re-ordered to minimize the total travel time. Keep in mind that the limits on the number of locations of the Route Optimization API applies, and the request costs more credits.  | [optional] if omitted the server will use the default value of "false"
 **instructions** | **bool**| If instructions should be calculated and returned  | [optional] if omitted the server will use the default value of True
 **calc_points** | **bool**| If the points for the route should be calculated at all.  | [optional] if omitted the server will use the default value of True
 **debug** | **bool**| If &#x60;true&#x60;, the output will be formatted.  | [optional] if omitted the server will use the default value of False
 **points_encoded** | **bool**| Allows changing the encoding of location data in the response. The default is polyline encoding, which is compact but requires special client code to unpack. (We provide it in our JavaScript client library!) Set this parameter to &#x60;false&#x60; to switch the encoding to simple coordinate pairs like &#x60;[lon,lat]&#x60;, or &#x60;[lon,lat,elevation]&#x60;. See the description of the response format for more information.  | [optional] if omitted the server will use the default value of True
 **ch_disable** | **bool**| Use this parameter in combination with one or more parameters from below.  | [optional] if omitted the server will use the default value of False
 **heading** | **[int]**| Favour a heading direction for a certain point. Specify either one heading for the start point or as many as there are points. In this case headings are associated by their order to the specific points. Headings are given as north based clockwise angle between 0 and 360 degree. This parameter also influences the tour generated with &#x60;algorithm&#x3D;round_trip&#x60; and forces the initial direction.  Requires &#x60;ch.disable&#x3D;true&#x60;.  | [optional]
 **heading_penalty** | **int**| Time penalty in seconds for not obeying a specified heading. Requires &#x60;ch.disable&#x3D;true&#x60;.  | [optional] if omitted the server will use the default value of 120
 **pass_through** | **bool**| If &#x60;true&#x60;, u-turns are avoided at via-points with regard to the &#x60;heading_penalty&#x60;. Requires &#x60;ch.disable&#x3D;true&#x60;.  | [optional] if omitted the server will use the default value of False
 **algorithm** | **str**| Rather than looking for the shortest or fastest path, this parameter lets you solve two different problems related to routing: With &#x60;alternative_route&#x60;, we give you not one but several routes that are close to optimal, but not too similar to each other.  With &#x60;round_trip&#x60;, the route will get you back to where you started. This is meant for fun (think of a bike trip), so we will add some randomness. The &#x60;round_trip&#x60; option requires &#x60;ch.disable&#x3D;true&#x60;. You can control both of these features with additional parameters, see below.   | [optional]
 **round_trip_distance** | **int**| If &#x60;algorithm&#x3D;round_trip&#x60;, this parameter configures approximative length of the resulting round trip. Requires &#x60;ch.disable&#x3D;true&#x60;.  | [optional] if omitted the server will use the default value of 10000
 **round_trip_seed** | **int**| If &#x60;algorithm&#x3D;round_trip&#x60;, this sets the random seed. Change this to get a different tour for each value.  | [optional]
 **alternative_route_max_paths** | **int**| If &#x60;algorithm&#x3D;alternative_route&#x60;, this parameter sets the number of maximum paths which should be calculated. Increasing can lead to worse alternatives.  | [optional] if omitted the server will use the default value of 2
 **alternative_route_max_weight_factor** | **float**| If &#x60;algorithm&#x3D;alternative_route&#x60;, this parameter sets the factor by which the alternatives routes can be longer than the optimal route. Increasing can lead to worse alternatives.  | [optional] if omitted the server will use the default value of 1.4
 **alternative_route_max_share_factor** | **float**| If &#x60;algorithm&#x3D;alternative_route&#x60;, this parameter specifies how similar an alternative route can be to the optimal route. Increasing can lead to worse alternatives.  | [optional] if omitted the server will use the default value of 0.6

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
**400** | Your request is not valid. For example, you specified too few or too many points. |  * X-RateLimit-Limit - Your current daily credit limit. <br>  * X-RateLimit-Remaining - Your remaining credits until the reset. <br>  * X-RateLimit-Reset - The number of seconds that you have to wait before a reset of the credit count is done. <br>  * X-RateLimit-Credits - The credit costs for this request. Note it could be a decimal and even negative number, e.g. when an async request failed. <br>  |
**401** | Authentication necessary |  * X-RateLimit-Limit - Your current daily credit limit. <br>  * X-RateLimit-Remaining - Your remaining credits until the reset. <br>  * X-RateLimit-Reset - The number of seconds that you have to wait before a reset of the credit count is done. <br>  * X-RateLimit-Credits - The credit costs for this request. Note it could be a decimal and even negative number, e.g. when an async request failed. <br>  |
**429** | API limit reached. |  * X-RateLimit-Limit - Your current daily credit limit. <br>  * X-RateLimit-Remaining - Your remaining credits until the reset. <br>  * X-RateLimit-Reset - The number of seconds that you have to wait before a reset of the credit count is done. <br>  * X-RateLimit-Credits - The credit costs for this request. Note it could be a decimal and even negative number, e.g. when an async request failed. <br>  |
**500** | Internal server error. We get notified automatically and fix this asap. |  * X-RateLimit-Limit - Your current daily credit limit. <br>  * X-RateLimit-Remaining - Your remaining credits until the reset. <br>  * X-RateLimit-Reset - The number of seconds that you have to wait before a reset of the credit count is done. <br>  * X-RateLimit-Credits - The credit costs for this request. Note it could be a decimal and even negative number, e.g. when an async request failed. <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_route**
> RouteResponse post_route()

POST Route Endpoint

Please see the [GET endpoint](#operation/getRoute) for alternative method on how to get started. If you are familiar with POST requests and JSON or you need the [`custom_model` Feature](#section/Custom-Model) then please continue here.  Especially when you use many locations you should get familiar with this POST endpoint as the GET endpoint has an URL length limitation. Additionally the request of this POST endpoint can be compressed and can slightly speed up the request.  To do a request you send JSON data. Both request scenarios GET and POST are identical except that all singular parameter names are named as their plural for a POST request. The effected parameters are: `points`, `point_hints` and `snap_preventions`.  **Please note that in opposite to the GET endpoint, points are specified in the order of `longitude, latitude`**.  For example `point=10,11&point=20,22` will be converted to the `points` array (plural): ```json { \"points\": [[11,10], [22,20]] } ``` Note again that also the order changes from `latitude,longitude` of the GET request to `[longitude,latitude]` for the POST request similar to [GeoJson](http://geojson.org/geojson-spec.html#examples).  Example: ```bash curl -X POST -H \"Content-Type: application/json\" \"https://graphhopper.com/api/1/route?key=[YOUR_KEY]\" -d '{\"elevation\":false,\"points\":[[-0.087891,51.534377],[-0.090637,51.467697]],\"vehicle\":\"car\"}' ``` 

### Example

* Api Key Authentication (api_key):

```python
import time
import openapi_client
from openapi_client.api import routing_api_api
from openapi_client.model.route_request import RouteRequest
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
    api_instance = routing_api_api.RoutingAPIApi(api_client)
    route_request = RouteRequest(
        profile="car",
        points=[[11.539421,48.118477],[11.559023,48.12228]],
        point_hints=["Lindenschmitstraße","Thalkirchener Str."],
        snap_preventions=["motorway","ferry","tunnel"],
        curbsides=["any","right"],
        locale="en",
        elevation=False,
        details=[
            "details_example",
        ],
        optimize="false",
        instructions=True,
        calc_points=True,
        debug=False,
        points_encoded=True,
        ch_disable=False,
        custom_model=CustomModel(
            speed=[
                {},
            ],
            priority=[
                {},
            ],
            distance_influence=70,
            areas={},
        ),
        headings=[
            1,
        ],
        heading_penalty=120,
        pass_through=False,
        algorithm="round_trip",
        round_trip_distance=10000,
        round_trip_seed=1,
        alternative_route_max_paths=2,
        alternative_route_max_weight_factor=1.4,
        alternative_route_max_share_factor=0.6,
    ) # RouteRequest |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # POST Route Endpoint
        api_response = api_instance.post_route(route_request=route_request)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling RoutingAPIApi->post_route: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **route_request** | [**RouteRequest**](RouteRequest.md)|  | [optional]

### Return type

[**RouteResponse**](RouteResponse.md)

### Authorization

[api_key](../README.md#api_key)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Routing Result |  * X-RateLimit-Limit - Your current daily credit limit. <br>  * X-RateLimit-Remaining - Your remaining credits until the reset. <br>  * X-RateLimit-Reset - The number of seconds that you have to wait before a reset of the credit count is done. <br>  * X-RateLimit-Credits - The credit costs for this request. Note it could be a decimal and even negative number, e.g. when an async request failed. <br>  |
**400** | Your request is not valid. For example, you specified too few or too many points. |  * X-RateLimit-Limit - Your current daily credit limit. <br>  * X-RateLimit-Remaining - Your remaining credits until the reset. <br>  * X-RateLimit-Reset - The number of seconds that you have to wait before a reset of the credit count is done. <br>  * X-RateLimit-Credits - The credit costs for this request. Note it could be a decimal and even negative number, e.g. when an async request failed. <br>  |
**401** | Authentication necessary |  * X-RateLimit-Limit - Your current daily credit limit. <br>  * X-RateLimit-Remaining - Your remaining credits until the reset. <br>  * X-RateLimit-Reset - The number of seconds that you have to wait before a reset of the credit count is done. <br>  * X-RateLimit-Credits - The credit costs for this request. Note it could be a decimal and even negative number, e.g. when an async request failed. <br>  |
**429** | API limit reached. |  * X-RateLimit-Limit - Your current daily credit limit. <br>  * X-RateLimit-Remaining - Your remaining credits until the reset. <br>  * X-RateLimit-Reset - The number of seconds that you have to wait before a reset of the credit count is done. <br>  * X-RateLimit-Credits - The credit costs for this request. Note it could be a decimal and even negative number, e.g. when an async request failed. <br>  |
**500** | Internal server error. We get notified automatically and fix this asap. |  * X-RateLimit-Limit - Your current daily credit limit. <br>  * X-RateLimit-Remaining - Your remaining credits until the reset. <br>  * X-RateLimit-Reset - The number of seconds that you have to wait before a reset of the credit count is done. <br>  * X-RateLimit-Credits - The credit costs for this request. Note it could be a decimal and even negative number, e.g. when an async request failed. <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **route_info_get**
> InfoResponse route_info_get()

Coverage information

Use this to find out details about the supported vehicle profiles and features, or if you just need to ping the server. 

### Example

* Api Key Authentication (api_key):

```python
import time
import openapi_client
from openapi_client.api import routing_api_api
from openapi_client.model.info_response import InfoResponse
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
    api_instance = routing_api_api.RoutingAPIApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Coverage information
        api_response = api_instance.route_info_get()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling RoutingAPIApi->route_info_get: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

[**InfoResponse**](InfoResponse.md)

### Authorization

[api_key](../README.md#api_key)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Coverage Information |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
