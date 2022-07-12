# openapi_client.ClusterAPIApi

All URIs are relative to *https://graphhopper.com/api/1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**async_clustering_problem**](ClusterAPIApi.md#async_clustering_problem) | **POST** /cluster/calculate | Batch Cluster Endpoint
[**get_cluster_solution**](ClusterAPIApi.md#get_cluster_solution) | **GET** /cluster/solution/{jobId} | GET Batch Solution Endpoint
[**solve_clustering_problem**](ClusterAPIApi.md#solve_clustering_problem) | **POST** /cluster | POST Cluster Endpoint


# **async_clustering_problem**
> JobId async_clustering_problem(cluster_request)

Batch Cluster Endpoint

 Prefer the [synchronous endpoint](#operation/solveClusteringProblem) and use this Batch Cluster endpoint for long running problems only. The work flow is asynchronous:  - send a POST request towards `https://graphhopper.com/api/1/cluster/calculate?key=<your_key>` and fetch the job_id. - poll the solution every 500ms until it gives `status=finished`. Do this with a GET request   towards `https://graphhopper.com/api/1/cluster/solution/<job_id>?key=<your_key>`. 

### Example

* Api Key Authentication (api_key):

```python
import time
import openapi_client
from openapi_client.api import cluster_api_api
from openapi_client.model.internal_error_message import InternalErrorMessage
from openapi_client.model.cluster_request import ClusterRequest
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
    api_instance = cluster_api_api.ClusterAPIApi(api_client)
    cluster_request = ClusterRequest(
        configuration=ClusterConfiguration(
            response_type="json",
            routing=ClusterConfigurationRouting(
                profile="car",
                cost_per_second=1,
                cost_per_meter=0,
            ),
            clustering=ClusterConfigurationClustering(
                num_clusters=10,
                max_quantity=50,
                min_quantity=30,
            ),
        ),
        clusters=[
            Clusters(
                name="GraphHopper GmbH",
                center=ClusterCustomerAddress(
                    lon=11.53941,
                    lat=48.118434,
                    street_hint="Lindenschmitstraße 52",
                ),
                min_quantity=10,
                max_quantity=10,
            ),
        ],
        customers=[
            ClusterCustomer(
                id="GraphHopper GmbH",
                address=ClusterCustomerAddress(
                    lon=11.53941,
                    lat=48.118434,
                    street_hint="Lindenschmitstraße 52",
                ),
                quantity=10,
            ),
        ],
    ) # ClusterRequest | Request object that contains the problem to be solved

    # example passing only required values which don't have defaults set
    try:
        # Batch Cluster Endpoint
        api_response = api_instance.async_clustering_problem(cluster_request)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ClusterAPIApi->async_clustering_problem: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cluster_request** | [**ClusterRequest**](ClusterRequest.md)| Request object that contains the problem to be solved |

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

# **get_cluster_solution**
> ClusterResponse get_cluster_solution(job_id)

GET Batch Solution Endpoint

This endpoint returns the solution of the clustering problems submitted to the [Batch Cluster endpoint](#operation/asyncClusteringProblem). You can fetch it with the job_id, you have been sent. 

### Example

* Api Key Authentication (api_key):

```python
import time
import openapi_client
from openapi_client.api import cluster_api_api
from openapi_client.model.bad_request import BadRequest
from openapi_client.model.cluster_response import ClusterResponse
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
    api_instance = cluster_api_api.ClusterAPIApi(api_client)
    job_id = "jobId_example" # str | Request solution with jobId

    # example passing only required values which don't have defaults set
    try:
        # GET Batch Solution Endpoint
        api_response = api_instance.get_cluster_solution(job_id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ClusterAPIApi->get_cluster_solution: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**| Request solution with jobId |

### Return type

[**ClusterResponse**](ClusterResponse.md)

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

# **solve_clustering_problem**
> ClusterResponse solve_clustering_problem(cluster_request)

POST Cluster Endpoint

 The Cluster endpoint is used with a POST request towards `https://graphhopper.com/api/1/cluster?key=<your_key>`. The solution will be provided in the JSON response. Please note that for problems that take longer than 10 seconds a bad request error is returned. In this case please use the asynchronous [Batch Cluster Endpoint](#operation/asyncClusteringProblem) instead. 

### Example

* Api Key Authentication (api_key):

```python
import time
import openapi_client
from openapi_client.api import cluster_api_api
from openapi_client.model.internal_error_message import InternalErrorMessage
from openapi_client.model.cluster_request import ClusterRequest
from openapi_client.model.bad_request import BadRequest
from openapi_client.model.cluster_response import ClusterResponse
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
    api_instance = cluster_api_api.ClusterAPIApi(api_client)
    cluster_request = ClusterRequest(
        configuration=ClusterConfiguration(
            response_type="json",
            routing=ClusterConfigurationRouting(
                profile="car",
                cost_per_second=1,
                cost_per_meter=0,
            ),
            clustering=ClusterConfigurationClustering(
                num_clusters=10,
                max_quantity=50,
                min_quantity=30,
            ),
        ),
        clusters=[
            Clusters(
                name="GraphHopper GmbH",
                center=ClusterCustomerAddress(
                    lon=11.53941,
                    lat=48.118434,
                    street_hint="Lindenschmitstraße 52",
                ),
                min_quantity=10,
                max_quantity=10,
            ),
        ],
        customers=[
            ClusterCustomer(
                id="GraphHopper GmbH",
                address=ClusterCustomerAddress(
                    lon=11.53941,
                    lat=48.118434,
                    street_hint="Lindenschmitstraße 52",
                ),
                quantity=10,
            ),
        ],
    ) # ClusterRequest | Request object that contains the problem to be solved

    # example passing only required values which don't have defaults set
    try:
        # POST Cluster Endpoint
        api_response = api_instance.solve_clustering_problem(cluster_request)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ClusterAPIApi->solve_clustering_problem: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cluster_request** | [**ClusterRequest**](ClusterRequest.md)| Request object that contains the problem to be solved |

### Return type

[**ClusterResponse**](ClusterResponse.md)

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

