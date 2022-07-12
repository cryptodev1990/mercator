# openapi_client.RouteOptimizationAPIApi

All URIs are relative to *https://graphhopper.com/api/1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**async_vrp**](RouteOptimizationAPIApi.md#async_vrp) | **POST** /vrp/optimize | POST route optimization problem (batch mode)
[**get_solution**](RouteOptimizationAPIApi.md#get_solution) | **GET** /vrp/solution/{jobId} | GET the solution (batch mode)
[**solve_vrp**](RouteOptimizationAPIApi.md#solve_vrp) | **POST** /vrp | POST route optimization problem


# **async_vrp**
> JobId async_vrp(request)

POST route optimization problem (batch mode)

 To solve a vehicle routing problem, perform the following steps:  1.) Make a HTTP POST to this URL  ``` https://graphhopper.com/api/1/vrp/optimize?key=<your_key> ```  It returns a job id (job_id).  2.) Take the job id and fetch the solution for the vehicle routing problem from this URL:  ``` https://graphhopper.com/api/1/vrp/solution/<job_id>?key=<your_key> ```  We recommend to query the solution every 500ms until it returns 'status=finished'.  **Note**: Since the workflow is a bit more cumbersome and since you lose some time in fetching the solution, you should always prefer the [synchronous endpoint](#operation/solveVRP). You should use the batch mode only for long running problems. 

### Example

* Api Key Authentication (api_key):

```python
import time
import openapi_client
from openapi_client.api import route_optimization_api_api
from openapi_client.model.internal_error_message import InternalErrorMessage
from openapi_client.model.request import Request
from openapi_client.model.bad_request import BadRequest
from openapi_client.model.job_id import JobId
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
    api_instance = route_optimization_api_api.RouteOptimizationAPIApi(api_client)
    request = Request(
        vehicles=[
            Vehicle(
                vehicle_id="vehicle-1",
                type_id="my-own-type",
                start_address=Address(
                    location_id="550e8400-e29b-11d4-a716-446655440000",
                    name="Queens Victoria Street 70, Second Floor, Flat 245",
                    lon=-0.092869,
                    lat=51.512665,
                    street_hint="Queens Victoria Street 70",
                    curbside="If you would like to arrive at this address without having to cross the street use `curbside=right/left` for countries with right/left-hand driving. Using `curbside=any` is the same as not specifying this parameter at all.",
                ),
                end_address=Address(
                    location_id="550e8400-e29b-11d4-a716-446655440000",
                    name="Queens Victoria Street 70, Second Floor, Flat 245",
                    lon=-0.092869,
                    lat=51.512665,
                    street_hint="Queens Victoria Street 70",
                    curbside="If you would like to arrive at this address without having to cross the street use `curbside=right/left` for countries with right/left-hand driving. Using `curbside=any` is the same as not specifying this parameter at all.",
                ),
                _break=VehicleBreak(None),
                return_to_depot=True,
                earliest_start=0,
                latest_end=1,
                skills=["drilling_maschine","screw_driver"],
                max_distance=400000,
                max_driving_time=28800,
                max_jobs=12,
                min_jobs=12,
                max_activities=24,
                move_to_end_address=True,
            ),
        ],
        vehicle_types=[
            VehicleType(
                type_id="my-own-type",
                profile="car",
                capacity=[100,500],
                speed_factor=1,
                service_time_factor=1,
                cost_per_meter=3.14,
                cost_per_second=3.14,
                cost_per_activation=3.14,
                consider_traffic=False,
                network_data_provider="openstreetmap",
            ),
        ],
        services=[
            Service(
                id="7fe77504-7df8-4497-843c-02d70b6490ce",
                type="delivery",
                priority=1,
                name="delivery pizza",
                address=Address(
                    location_id="550e8400-e29b-11d4-a716-446655440000",
                    name="Queens Victoria Street 70, Second Floor, Flat 245",
                    lon=-0.092869,
                    lat=51.512665,
                    street_hint="Queens Victoria Street 70",
                    curbside="If you would like to arrive at this address without having to cross the street use `curbside=right/left` for countries with right/left-hand driving. Using `curbside=any` is the same as not specifying this parameter at all.",
                ),
                duration=1800,
                preparation_time=300,
                time_windows=[
                    TimeWindow(
                        earliest=0,
                        latest=1,
                    ),
                ],
                size=[30,5,1],
                required_skills=["drilling_machine","screw_driver"],
                allowed_vehicles=["technician_peter","technician_stefan"],
                disallowed_vehicles=["driver-A","driver-B"],
                max_time_in_vehicle=900,
                group="group-A",
            ),
        ],
        shipments=[
            Shipment(
                id="7fe77504-7df8-4497-843c-02d70b6490ce",
                name="pickup and deliver pizza to Peter",
                priority=1,
                pickup=Stop(
                    address=Address(
                        location_id="550e8400-e29b-11d4-a716-446655440000",
                        name="Queens Victoria Street 70, Second Floor, Flat 245",
                        lon=-0.092869,
                        lat=51.512665,
                        street_hint="Queens Victoria Street 70",
                        curbside="If you would like to arrive at this address without having to cross the street use `curbside=right/left` for countries with right/left-hand driving. Using `curbside=any` is the same as not specifying this parameter at all.",
                    ),
                    duration=1800,
                    preparation_time=300,
                    time_windows=[
                        TimeWindow(
                            earliest=0,
                            latest=1,
                        ),
                    ],
                    group="ASAP",
                ),
                delivery=Stop(
                    address=Address(
                        location_id="550e8400-e29b-11d4-a716-446655440000",
                        name="Queens Victoria Street 70, Second Floor, Flat 245",
                        lon=-0.092869,
                        lat=51.512665,
                        street_hint="Queens Victoria Street 70",
                        curbside="If you would like to arrive at this address without having to cross the street use `curbside=right/left` for countries with right/left-hand driving. Using `curbside=any` is the same as not specifying this parameter at all.",
                    ),
                    duration=1800,
                    preparation_time=300,
                    time_windows=[
                        TimeWindow(
                            earliest=0,
                            latest=1,
                        ),
                    ],
                    group="ASAP",
                ),
                size=[3],
                required_skills=["drilling_machine","screw_driver"],
                allowed_vehicles=["technician_peter","technician_stefan"],
                disallowed_vehicles=["driver-A","driver-B"],
                max_time_in_vehicle=1800,
            ),
        ],
        relations=[
            RequestRelationsInner(None),
        ],
        algorithm=Algorithm(
            problem_type="min",
            objective="transport_time",
        ),
        objectives=[
            Objective(
                type="min",
                value="transport_time",
            ),
        ],
        cost_matrices=[
            CostMatrix(
                type="default",
                location_ids=[
                    "location_ids_example",
                ],
                data=CostMatrixData(
                    times=[
                        [
                            1,
                        ],
                    ],
                    distances=[
                        [
                            3.14,
                        ],
                    ],
                    info=CostMatrixDataInfo(
                        copyrights=[
                            "copyrights_example",
                        ],
                        took=3.14,
                    ),
                ),
                profile="profile_example",
            ),
        ],
        configuration=Configuration(
            routing=Routing(
                calc_points=False,
                consider_traffic=False,
                network_data_provider="openstreetmap",
                curbside_strictness="soft",
                fail_fast=True,
                return_snapped_waypoints=False,
                snap_preventions=["motorway","trunk","bridge","tunnel","ferry"],
            ),
        ),
    ) # Request | The request that contains the problem to be solved.

    # example passing only required values which don't have defaults set
    try:
        # POST route optimization problem (batch mode)
        api_response = api_instance.async_vrp(request)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling RouteOptimizationAPIApi->async_vrp: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request** | [**Request**](Request.md)| The request that contains the problem to be solved. |

### Return type

[**JobId**](JobId.md)

### Authorization

[api_key](../README.md#api_key)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A jobId you can use to retrieve your solution from the server - see solution endpoint. |  * X-RateLimit-Limit - Your current daily credit limit. <br>  * X-RateLimit-Remaining - Your remaining credits until the reset. <br>  * X-RateLimit-Reset - The number of seconds that you have to wait before a reset of the credit count is done. <br>  * X-RateLimit-Credits - The credit costs for this request. Note it could be a decimal and even negative number, e.g. when an async request failed. <br>  |
**400** | Error occurred when reading client request. Request is invalid. |  -  |
**500** | Error occurred on server side. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_solution**
> Response get_solution(job_id)

GET the solution (batch mode)

 Take the job id and fetch the solution for the vehicle routing problem from this URL:  ``` https://graphhopper.com/api/1/vrp/solution/<job_id>?key=<your_key> ```  You get the job id by sending a vehicle routing problem to the [batch mode URL](#operation/asyncVRP). 

### Example

* Api Key Authentication (api_key):

```python
import time
import openapi_client
from openapi_client.api import route_optimization_api_api
from openapi_client.model.response import Response
from openapi_client.model.bad_request import BadRequest
from openapi_client.model.get_solution404_response import GetSolution404Response
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
    api_instance = route_optimization_api_api.RouteOptimizationAPIApi(api_client)
    job_id = "jobId_example" # str | Request solution with jobId

    # example passing only required values which don't have defaults set
    try:
        # GET the solution (batch mode)
        api_response = api_instance.get_solution(job_id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling RouteOptimizationAPIApi->get_solution: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**| Request solution with jobId |

### Return type

[**Response**](Response.md)

### Authorization

[api_key](../README.md#api_key)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A response containing the solution |  * X-RateLimit-Limit - Your current daily credit limit. <br>  * X-RateLimit-Remaining - Your remaining credits until the reset. <br>  * X-RateLimit-Reset - The number of seconds that you have to wait before a reset of the credit count is done. <br>  * X-RateLimit-Credits - The credit costs for this request. Note it could be a decimal and even negative number, e.g. when an async request failed. <br>  |
**400** | Error occurred on client side such as invalid input. |  -  |
**404** | Requested solution could not be found. |  -  |
**500** | Error occurred on server side. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **solve_vrp**
> Response solve_vrp(request)

POST route optimization problem

 To get started with the Route Optimization API, please read the [introduction](#tag/Route-Optimization-API).  To solve a new vehicle routing problem, make a HTTP POST to this URL  ``` https://graphhopper.com/api/1/vrp?key=<your_key> ```  It returns the solution to this problem in the JSON response.  Please note that this URL is very well suited to solve minor problems. Larger vehicle routing problems, which take longer than 10 seconds to solve, cannot be solved. To solve them, please use the [batch mode URL](#operation/asyncVRP) instead. 

### Example

* Api Key Authentication (api_key):

```python
import time
import openapi_client
from openapi_client.api import route_optimization_api_api
from openapi_client.model.internal_error_message import InternalErrorMessage
from openapi_client.model.response import Response
from openapi_client.model.request import Request
from openapi_client.model.bad_request import BadRequest
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
    api_instance = route_optimization_api_api.RouteOptimizationAPIApi(api_client)
    request = Request(
        vehicles=[
            Vehicle(
                vehicle_id="vehicle-1",
                type_id="my-own-type",
                start_address=Address(
                    location_id="550e8400-e29b-11d4-a716-446655440000",
                    name="Queens Victoria Street 70, Second Floor, Flat 245",
                    lon=-0.092869,
                    lat=51.512665,
                    street_hint="Queens Victoria Street 70",
                    curbside="If you would like to arrive at this address without having to cross the street use `curbside=right/left` for countries with right/left-hand driving. Using `curbside=any` is the same as not specifying this parameter at all.",
                ),
                end_address=Address(
                    location_id="550e8400-e29b-11d4-a716-446655440000",
                    name="Queens Victoria Street 70, Second Floor, Flat 245",
                    lon=-0.092869,
                    lat=51.512665,
                    street_hint="Queens Victoria Street 70",
                    curbside="If you would like to arrive at this address without having to cross the street use `curbside=right/left` for countries with right/left-hand driving. Using `curbside=any` is the same as not specifying this parameter at all.",
                ),
                _break=VehicleBreak(None),
                return_to_depot=True,
                earliest_start=0,
                latest_end=1,
                skills=["drilling_maschine","screw_driver"],
                max_distance=400000,
                max_driving_time=28800,
                max_jobs=12,
                min_jobs=12,
                max_activities=24,
                move_to_end_address=True,
            ),
        ],
        vehicle_types=[
            VehicleType(
                type_id="my-own-type",
                profile="car",
                capacity=[100,500],
                speed_factor=1,
                service_time_factor=1,
                cost_per_meter=3.14,
                cost_per_second=3.14,
                cost_per_activation=3.14,
                consider_traffic=False,
                network_data_provider="openstreetmap",
            ),
        ],
        services=[
            Service(
                id="7fe77504-7df8-4497-843c-02d70b6490ce",
                type="delivery",
                priority=1,
                name="delivery pizza",
                address=Address(
                    location_id="550e8400-e29b-11d4-a716-446655440000",
                    name="Queens Victoria Street 70, Second Floor, Flat 245",
                    lon=-0.092869,
                    lat=51.512665,
                    street_hint="Queens Victoria Street 70",
                    curbside="If you would like to arrive at this address without having to cross the street use `curbside=right/left` for countries with right/left-hand driving. Using `curbside=any` is the same as not specifying this parameter at all.",
                ),
                duration=1800,
                preparation_time=300,
                time_windows=[
                    TimeWindow(
                        earliest=0,
                        latest=1,
                    ),
                ],
                size=[30,5,1],
                required_skills=["drilling_machine","screw_driver"],
                allowed_vehicles=["technician_peter","technician_stefan"],
                disallowed_vehicles=["driver-A","driver-B"],
                max_time_in_vehicle=900,
                group="group-A",
            ),
        ],
        shipments=[
            Shipment(
                id="7fe77504-7df8-4497-843c-02d70b6490ce",
                name="pickup and deliver pizza to Peter",
                priority=1,
                pickup=Stop(
                    address=Address(
                        location_id="550e8400-e29b-11d4-a716-446655440000",
                        name="Queens Victoria Street 70, Second Floor, Flat 245",
                        lon=-0.092869,
                        lat=51.512665,
                        street_hint="Queens Victoria Street 70",
                        curbside="If you would like to arrive at this address without having to cross the street use `curbside=right/left` for countries with right/left-hand driving. Using `curbside=any` is the same as not specifying this parameter at all.",
                    ),
                    duration=1800,
                    preparation_time=300,
                    time_windows=[
                        TimeWindow(
                            earliest=0,
                            latest=1,
                        ),
                    ],
                    group="ASAP",
                ),
                delivery=Stop(
                    address=Address(
                        location_id="550e8400-e29b-11d4-a716-446655440000",
                        name="Queens Victoria Street 70, Second Floor, Flat 245",
                        lon=-0.092869,
                        lat=51.512665,
                        street_hint="Queens Victoria Street 70",
                        curbside="If you would like to arrive at this address without having to cross the street use `curbside=right/left` for countries with right/left-hand driving. Using `curbside=any` is the same as not specifying this parameter at all.",
                    ),
                    duration=1800,
                    preparation_time=300,
                    time_windows=[
                        TimeWindow(
                            earliest=0,
                            latest=1,
                        ),
                    ],
                    group="ASAP",
                ),
                size=[3],
                required_skills=["drilling_machine","screw_driver"],
                allowed_vehicles=["technician_peter","technician_stefan"],
                disallowed_vehicles=["driver-A","driver-B"],
                max_time_in_vehicle=1800,
            ),
        ],
        relations=[
            RequestRelationsInner(None),
        ],
        algorithm=Algorithm(
            problem_type="min",
            objective="transport_time",
        ),
        objectives=[
            Objective(
                type="min",
                value="transport_time",
            ),
        ],
        cost_matrices=[
            CostMatrix(
                type="default",
                location_ids=[
                    "location_ids_example",
                ],
                data=CostMatrixData(
                    times=[
                        [
                            1,
                        ],
                    ],
                    distances=[
                        [
                            3.14,
                        ],
                    ],
                    info=CostMatrixDataInfo(
                        copyrights=[
                            "copyrights_example",
                        ],
                        took=3.14,
                    ),
                ),
                profile="profile_example",
            ),
        ],
        configuration=Configuration(
            routing=Routing(
                calc_points=False,
                consider_traffic=False,
                network_data_provider="openstreetmap",
                curbside_strictness="soft",
                fail_fast=True,
                return_snapped_waypoints=False,
                snap_preventions=["motorway","trunk","bridge","tunnel","ferry"],
            ),
        ),
    ) # Request | The request that contains the vehicle routing problem to be solved.

    # example passing only required values which don't have defaults set
    try:
        # POST route optimization problem
        api_response = api_instance.solve_vrp(request)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling RouteOptimizationAPIApi->solve_vrp: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request** | [**Request**](Request.md)| The request that contains the vehicle routing problem to be solved. |

### Return type

[**Response**](Response.md)

### Authorization

[api_key](../README.md#api_key)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A response containing the solution |  * X-RateLimit-Limit - Your current daily credit limit. <br>  * X-RateLimit-Remaining - Your remaining credits until the reset. <br>  * X-RateLimit-Reset - The number of seconds that you have to wait before a reset of the credit count is done. <br>  * X-RateLimit-Credits - The credit costs for this request. Note it could be a decimal and even negative number, e.g. when an async request failed. <br>  |
**400** | Error occurred when reading the request. Request is invalid. |  -  |
**500** | Error occurred on server side. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

