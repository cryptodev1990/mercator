# MatrixRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**profile** | **str** | Specifies the vehicle profile of this type. The profile is used to determine the network, speed and other physical attributes to use for routing the vehicle or pedestrian. See the section about [routing profiles](#section/Map-Data-and-Routing-Profiles) for more details and valid profile values. | [optional]  if omitted the server will use the default value of "car"
**from_points** | **[[float]]** | The starting points for the routes in an array of &#x60;[longitude,latitude]&#x60;. For instance, if you want to calculate three routes from point A such as A-&gt;1, A-&gt;2, A-&gt;3 then you have one &#x60;from_point&#x60; parameter and three &#x60;to_point&#x60; parameters. | [optional] 
**to_points** | **[[float]]** | The destination points for the routes in an array of &#x60;[longitude,latitude]&#x60;. | [optional] 
**from_point_hints** | **[str]** | See &#x60;point_hints&#x60;of symmetrical matrix | [optional] 
**to_point_hints** | **[str]** | See &#x60;point_hints&#x60;of symmetrical matrix | [optional] 
**snap_preventions** | **[str]** | See &#x60;snap_preventions&#x60; of symmetrical matrix | [optional] 
**from_curbsides** | **[str]** | See &#x60;curbsides&#x60;of symmetrical matrix | [optional] 
**to_curbsides** | **[str]** | See &#x60;curbsides&#x60;of symmetrical matrix | [optional] 
**out_arrays** | **[str]** | Specifies which matrices should be included in the response. Specify one or more of the following options &#x60;weights&#x60;, &#x60;times&#x60;, &#x60;distances&#x60;. The units of the entries of &#x60;distances&#x60; are meters, of &#x60;times&#x60; are seconds and of &#x60;weights&#x60; is arbitrary and it can differ for different vehicles or versions of this API. | [optional] 
**fail_fast** | **bool** | Specifies whether or not the matrix calculation should return with an error as soon as possible in case some points cannot be found or some points are not connected. If set to &#x60;false&#x60; the time/weight/distance matrix will be calculated for all valid points and contain the &#x60;null&#x60; value for all entries that could not be calculated. The &#x60;hint&#x60; field of the response will also contain additional information about what went wrong (see its documentation). | [optional]  if omitted the server will use the default value of True
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


