# openapi_client.IsochroneAPIApi

All URIs are relative to *https://graphhopper.com/api/1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_isochrone**](IsochroneAPIApi.md#get_isochrone) | **GET** /isochrone | Isochrone Endpoint


# **get_isochrone**
> IsochroneResponse get_isochrone(point)

Isochrone Endpoint

### Example You can get an example response via:  ``` curl \"https://graphhopper.com/api/1/isochrone?point=51.131108,12.414551&key=[YOUR_KEY]\" ```  Don't forget to replace the placeholder with your own key.  ### Introduction ![Isochrone screenshot](./img/isochrone-example.png)  An isochrone of a location is ''a line connecting points at which a vehicle arrives at the same time'', see Wikipedia. With the same API you can also calculate isodistances, just use the parameter distance_limit instead of time_limit`.  ### Use Cases Some possible areas in which this API may be useful to you:  - real estate analysis - realtors - vehicle scheduling - geomarketing - reach of electric vehicles - transport planning - logistics (distribution and retail network planning)  ### API Clients and Examples See the [clients](#section/API-Clients) section in the main documentation, and [live examples](https://graphhopper.com/api/1/examples/#isochrone). 

### Example

* Api Key Authentication (api_key):

```python
import time
import openapi_client
from openapi_client.api import isochrone_api_api
from openapi_client.model.isochrone_response import IsochroneResponse
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
    api_instance = isochrone_api_api.IsochroneAPIApi(api_client)
    point = "point_example" # str | Specify the start coordinate
    time_limit = 600 # int | Specify which time the vehicle should travel. In seconds. (optional) if omitted the server will use the default value of 600
    distance_limit = 1 # int | Specify which distance the vehicle should travel. In meters. (optional)
    profile = "car" # str |  (optional) if omitted the server will use the default value of "car"
    buckets = 1 # int | Number by which to divide the given `time_limit` to create `buckets` nested isochrones of time intervals `time_limit-n*time_limit/buckets`. Applies analogously to `distance_limit`. (optional) if omitted the server will use the default value of 1
    reverse_flow = False # bool | If `false` the flow goes from point to the polygon, if `true` the flow goes from the polygon \"inside\" to the point. Example use case for `false`&#58; *How many potential customer can be reached within 30min travel time from your store* vs. `true`&#58; *How many customers can reach your store within 30min travel time.*  (optional) if omitted the server will use the default value of False

    # example passing only required values which don't have defaults set
    try:
        # Isochrone Endpoint
        api_response = api_instance.get_isochrone(point)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling IsochroneAPIApi->get_isochrone: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Isochrone Endpoint
        api_response = api_instance.get_isochrone(point, time_limit=time_limit, distance_limit=distance_limit, profile=profile, buckets=buckets, reverse_flow=reverse_flow)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling IsochroneAPIApi->get_isochrone: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **point** | **str**| Specify the start coordinate |
 **time_limit** | **int**| Specify which time the vehicle should travel. In seconds. | [optional] if omitted the server will use the default value of 600
 **distance_limit** | **int**| Specify which distance the vehicle should travel. In meters. | [optional]
 **profile** | **str**|  | [optional] if omitted the server will use the default value of "car"
 **buckets** | **int**| Number by which to divide the given &#x60;time_limit&#x60; to create &#x60;buckets&#x60; nested isochrones of time intervals &#x60;time_limit-n*time_limit/buckets&#x60;. Applies analogously to &#x60;distance_limit&#x60;. | [optional] if omitted the server will use the default value of 1
 **reverse_flow** | **bool**| If &#x60;false&#x60; the flow goes from point to the polygon, if &#x60;true&#x60; the flow goes from the polygon \&quot;inside\&quot; to the point. Example use case for &#x60;false&#x60;&amp;#58; *How many potential customer can be reached within 30min travel time from your store* vs. &#x60;true&#x60;&amp;#58; *How many customers can reach your store within 30min travel time.*  | [optional] if omitted the server will use the default value of False

### Return type

[**IsochroneResponse**](IsochroneResponse.md)

### Authorization

[api_key](../README.md#api_key)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Isochrone Result |  -  |
**0** | Unexpected Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

