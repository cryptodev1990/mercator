# openapi_client.GeocodingAPIApi

All URIs are relative to *https://graphhopper.com/api/1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_geocode**](GeocodingAPIApi.md#get_geocode) | **GET** /geocode | Geocoding Endpoint


# **get_geocode**
> GeocodingResponse get_geocode()

Geocoding Endpoint

 ### Introduction  ![Geocoding Example](./img/geocoding-example.png)  _Geocoding_ describes the process of transforming an textual address representation to a coordinate (`latitude,longitude`). For example the conversion from `Berlin` to `52.5170365,13.3888599`.  _Reverse geocoding_ converts a coordinate to a textual address representation or place name. Find out more about Geocoding itself on [Wikipedia](http://en.wikipedia.org/wiki/Geocoding). 

### Example

* Api Key Authentication (api_key):

```python
import time
import openapi_client
from openapi_client.api import geocoding_api_api
from openapi_client.model.geocoding_response import GeocodingResponse
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
    api_instance = geocoding_api_api.GeocodingAPIApi(api_client)
    q = "q_example" # str | If you do forward geocoding, this is `required` and is a textual description of the address you are looking for. (optional)
    locale = "en" # str | Display the search results for the specified locale. Currently French (fr), English (en), German (de) and Italian (it) are supported. If the locale wasn't found the default (en) is used. (optional) if omitted the server will use the default value of "en"
    limit = 10 # int | Specify the maximum number of results to return (optional) if omitted the server will use the default value of 10
    reverse = False # bool | It is `required` to be `true` if you want to do a reverse geocoding request. If it is `true`, `point` must be defined as well, and `q` must not be used. (optional) if omitted the server will use the default value of False
    debug = False # bool | If `true`, the output will be formatted. (optional) if omitted the server will use the default value of False
    point = "point_example" # str | _Forward geocoding_: The location bias in the format 'latitude,longitude' e.g. point=45.93272,11.58803. _Reverse geocoding_: The location to find amenities, cities. (optional)
    provider = "default" # str | The provider parameter is currently under development and can fall back to `default` at any time. The intend is to provide alternatives to our default geocoder. Each provider has its own strenghts and might fit better for certain scenarios, so it's worth to compare the different providers. To try it append the `provider`parameter to the URL like `&provider=nominatim`, the result structure should be identical in all cases - if not, please report this back to us. Keep in mind that some providers do not support certain parameters or don't return some fields, for example `osm_id` and `osm_type` are not supported by every geocoding provider. If you would like to use additional parameters of one of the providers, but it's not available for the GraphHopper Geocoding API, yet? Please contact us.  The credit costs can be different for all providers - see [here](https://support.graphhopper.com/support/solutions/articles/44000718211-what-is-one-credit-) for more information about it.  Currently, only the default provider and gisgraphy supports autocompletion of partial search strings.  All providers support normal \"forward\" geocoding and reverse geocoding via `reverse=true`.  #### Default (`provider=default`)  This provider returns results of our internal geocoding engine, as described above. In addition to the above documented parameters the following parameters are possible: * `bbox` - the expected format is `minLon,minLat,maxLon,maxLat` * `osm_tag` - you can filter `key:value` or exclude places with certain OpenStreetMap tags `!key:value`. E.g. `osm_tag=tourism:museum` or just the key `osm_tag=tourism`. To exclude multiple tags you add multiple `osm_tag` parameters.  #### Nominatim (`provider=nominatim`)  The GraphHopper Directions API uses a commercially hosted Nominatim geocoder (hosted by [OpenCageData](https://opencagedata.com/)).  In addition to the above documented parameters we currently support the following parameters:  * countrycode - The country code is a two letter code as defined by the ISO 3166-1 Alpha 2 standard. E.g. gb for the United Kingdom, fr for France, us for United States. * bounds - the expected format is `minLon,minLat,maxLon,maxLat`  #### Gisgraphy (`provider=gisgraphy`)  This provider returns results from the Gisgraphy geocoder which you can try [here](https://services.gisgraphy.com/static/leaflet/index.html).  **Limitations:** The `locale` parameter is not supported. Gisgraphy does not return OSM tags or an extent.  Gisgraphy has a special autocomplete API, which you can use by adding `autocomplete=true` (does not work with `reverse=true`). The autocomplete API is optimized on predicting text input, but returns less information.  In addition to the above documented parameters Gisgraphy allows to use the following parameters, which can be used as documented [here](https://www.gisgraphy.com/documentation/user-guide.php#geocodingservice):  * `radius` - radius in meters * `country` - restrict search for the specified country. The value must be the ISO 3166 Alpha 2 code of the country.  #### NetToolKit (`provider=nettoolkit`)  This provider returns results from the NetToolKit provider which is specialized for US addresses and provides a wrapper around Nominatim for other addresses. You can try it [here](https://www.nettoolkit.com/geo/demo).  The following additional NetToolKit parameters are supported (read [here](https://www.nettoolkit.com/docs/geo/geocoding) for more details): - `source`: User can choose which source provider to geocode the address, this value is \"NetToolKit\" by default - `country_code`: an iso-3166-2 country code (e.g : US) filter the results to the specify country code  **Limitations:** NetToolKit does not support the `locale` parameter. NetToolKit does not return OSM tags (e.g. osm_id, osm_type, osm_value).  #### OpenCage Data (`provider=opencagedata`)  This provider returns results from the OpenCageData geocoder which you can try [here](https://geocoder.opencagedata.com/demo). The difference to the `nominatim` provider is that [other geocoders](https://opencagedata.com/credits) might be used under the hood.  In addition to the above documented parameters OpenCage Data allows to use the following parameters, which can be used as documented [here](https://geocoder.opencagedata.com/api#forward-opt):  * countrycode - The country code is a two letter code as defined by the ISO 3166-1 Alpha 2 standard. E.g. gb for the United Kingdom, fr for France, us for United States.  * bounds - the expected format is `minLon,minLat,maxLon,maxLat`  (optional) if omitted the server will use the default value of "default"

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Geocoding Endpoint
        api_response = api_instance.get_geocode(q=q, locale=locale, limit=limit, reverse=reverse, debug=debug, point=point, provider=provider)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling GeocodingAPIApi->get_geocode: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **q** | **str**| If you do forward geocoding, this is &#x60;required&#x60; and is a textual description of the address you are looking for. | [optional]
 **locale** | **str**| Display the search results for the specified locale. Currently French (fr), English (en), German (de) and Italian (it) are supported. If the locale wasn&#39;t found the default (en) is used. | [optional] if omitted the server will use the default value of "en"
 **limit** | **int**| Specify the maximum number of results to return | [optional] if omitted the server will use the default value of 10
 **reverse** | **bool**| It is &#x60;required&#x60; to be &#x60;true&#x60; if you want to do a reverse geocoding request. If it is &#x60;true&#x60;, &#x60;point&#x60; must be defined as well, and &#x60;q&#x60; must not be used. | [optional] if omitted the server will use the default value of False
 **debug** | **bool**| If &#x60;true&#x60;, the output will be formatted. | [optional] if omitted the server will use the default value of False
 **point** | **str**| _Forward geocoding_: The location bias in the format &#39;latitude,longitude&#39; e.g. point&#x3D;45.93272,11.58803. _Reverse geocoding_: The location to find amenities, cities. | [optional]
 **provider** | **str**| The provider parameter is currently under development and can fall back to &#x60;default&#x60; at any time. The intend is to provide alternatives to our default geocoder. Each provider has its own strenghts and might fit better for certain scenarios, so it&#39;s worth to compare the different providers. To try it append the &#x60;provider&#x60;parameter to the URL like &#x60;&amp;provider&#x3D;nominatim&#x60;, the result structure should be identical in all cases - if not, please report this back to us. Keep in mind that some providers do not support certain parameters or don&#39;t return some fields, for example &#x60;osm_id&#x60; and &#x60;osm_type&#x60; are not supported by every geocoding provider. If you would like to use additional parameters of one of the providers, but it&#39;s not available for the GraphHopper Geocoding API, yet? Please contact us.  The credit costs can be different for all providers - see [here](https://support.graphhopper.com/support/solutions/articles/44000718211-what-is-one-credit-) for more information about it.  Currently, only the default provider and gisgraphy supports autocompletion of partial search strings.  All providers support normal \&quot;forward\&quot; geocoding and reverse geocoding via &#x60;reverse&#x3D;true&#x60;.  #### Default (&#x60;provider&#x3D;default&#x60;)  This provider returns results of our internal geocoding engine, as described above. In addition to the above documented parameters the following parameters are possible: * &#x60;bbox&#x60; - the expected format is &#x60;minLon,minLat,maxLon,maxLat&#x60; * &#x60;osm_tag&#x60; - you can filter &#x60;key:value&#x60; or exclude places with certain OpenStreetMap tags &#x60;!key:value&#x60;. E.g. &#x60;osm_tag&#x3D;tourism:museum&#x60; or just the key &#x60;osm_tag&#x3D;tourism&#x60;. To exclude multiple tags you add multiple &#x60;osm_tag&#x60; parameters.  #### Nominatim (&#x60;provider&#x3D;nominatim&#x60;)  The GraphHopper Directions API uses a commercially hosted Nominatim geocoder (hosted by [OpenCageData](https://opencagedata.com/)).  In addition to the above documented parameters we currently support the following parameters:  * countrycode - The country code is a two letter code as defined by the ISO 3166-1 Alpha 2 standard. E.g. gb for the United Kingdom, fr for France, us for United States. * bounds - the expected format is &#x60;minLon,minLat,maxLon,maxLat&#x60;  #### Gisgraphy (&#x60;provider&#x3D;gisgraphy&#x60;)  This provider returns results from the Gisgraphy geocoder which you can try [here](https://services.gisgraphy.com/static/leaflet/index.html).  **Limitations:** The &#x60;locale&#x60; parameter is not supported. Gisgraphy does not return OSM tags or an extent.  Gisgraphy has a special autocomplete API, which you can use by adding &#x60;autocomplete&#x3D;true&#x60; (does not work with &#x60;reverse&#x3D;true&#x60;). The autocomplete API is optimized on predicting text input, but returns less information.  In addition to the above documented parameters Gisgraphy allows to use the following parameters, which can be used as documented [here](https://www.gisgraphy.com/documentation/user-guide.php#geocodingservice):  * &#x60;radius&#x60; - radius in meters * &#x60;country&#x60; - restrict search for the specified country. The value must be the ISO 3166 Alpha 2 code of the country.  #### NetToolKit (&#x60;provider&#x3D;nettoolkit&#x60;)  This provider returns results from the NetToolKit provider which is specialized for US addresses and provides a wrapper around Nominatim for other addresses. You can try it [here](https://www.nettoolkit.com/geo/demo).  The following additional NetToolKit parameters are supported (read [here](https://www.nettoolkit.com/docs/geo/geocoding) for more details): - &#x60;source&#x60;: User can choose which source provider to geocode the address, this value is \&quot;NetToolKit\&quot; by default - &#x60;country_code&#x60;: an iso-3166-2 country code (e.g : US) filter the results to the specify country code  **Limitations:** NetToolKit does not support the &#x60;locale&#x60; parameter. NetToolKit does not return OSM tags (e.g. osm_id, osm_type, osm_value).  #### OpenCage Data (&#x60;provider&#x3D;opencagedata&#x60;)  This provider returns results from the OpenCageData geocoder which you can try [here](https://geocoder.opencagedata.com/demo). The difference to the &#x60;nominatim&#x60; provider is that [other geocoders](https://opencagedata.com/credits) might be used under the hood.  In addition to the above documented parameters OpenCage Data allows to use the following parameters, which can be used as documented [here](https://geocoder.opencagedata.com/api#forward-opt):  * countrycode - The country code is a two letter code as defined by the ISO 3166-1 Alpha 2 standard. E.g. gb for the United Kingdom, fr for France, us for United States.  * bounds - the expected format is &#x60;minLon,minLat,maxLon,maxLat&#x60;  | [optional] if omitted the server will use the default value of "default"

### Return type

[**GeocodingResponse**](GeocodingResponse.md)

### Authorization

[api_key](../README.md#api_key)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | An array found locations |  * X-RateLimit-Limit - Your current daily credit limit. <br>  * X-RateLimit-Remaining - Your remaining credits until the reset. <br>  * X-RateLimit-Reset - The number of seconds that you have to wait before a reset of the credit count is done. <br>  * X-RateLimit-Credits - The credit costs for this request. Note it could be a decimal and even negative number, e.g. when an async request failed. <br>  |
**0** | Unexpected error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

