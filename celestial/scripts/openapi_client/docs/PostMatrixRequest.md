# PostMatrixRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**profile** | **str** | Specifies the vehicle profile of this type. The profile is used to determine the network, speed and other physical attributes to use for routing the vehicle or pedestrian. See the section about [routing profiles](#section/Map-Data-and-Routing-Profiles) for more details and valid profile values. | [optional]  if omitted the server will use the default value of "car"
**from_points** | **[[float]]** | The starting points for the routes in an array of &#x60;[longitude,latitude]&#x60;. For instance, if you want to calculate three routes from point A such as A-&gt;1, A-&gt;2, A-&gt;3 then you have one &#x60;from_point&#x60; parameter and three &#x60;to_point&#x60; parameters. | [optional] 
**to_points** | **[[float]]** | The destination points for the routes in an array of &#x60;[longitude,latitude]&#x60;. | [optional] 
**from_point_hints** | **[str]** | See &#x60;point_hints&#x60;of symmetrical matrix | [optional] 
**to_point_hints** | **[str]** | See &#x60;point_hints&#x60;of symmetrical matrix | [optional] 
**snap_preventions** | **[str]** | Optional parameter to avoid snapping to a certain road class or road environment. Current supported values &#x60;motorway&#x60;, &#x60;trunk&#x60;, &#x60;ferry&#x60;, &#x60;tunnel&#x60;, &#x60;bridge&#x60; and &#x60;ford&#x60;. Please note that this feature does not e.g. avoid motorways for the route - it only avoids it for the \&quot;location snap\&quot;. | [optional] 
**from_curbsides** | **[str]** | See &#x60;curbsides&#x60;of symmetrical matrix | [optional] 
**to_curbsides** | **[str]** | See &#x60;curbsides&#x60;of symmetrical matrix | [optional] 
**out_arrays** | **[str]** | Specifies which matrices should be included in the response. Specify one or more of the following options &#x60;weights&#x60;, &#x60;times&#x60;, &#x60;distances&#x60;. The units of the entries of &#x60;distances&#x60; are meters, of &#x60;times&#x60; are seconds and of &#x60;weights&#x60; is arbitrary and it can differ for different vehicle profiles or versions of this API. | [optional] 
**fail_fast** | **bool** | Specifies whether or not the matrix calculation should return with an error as soon as possible in case some points cannot be found or some points are not connected. If set to &#x60;false&#x60; the time/weight/distance matrix will be calculated for all valid points and contain the &#x60;null&#x60; value for all entries that could not be calculated. The &#x60;hint&#x60; field of the response will also contain additional information about what went wrong (see its documentation). | [optional]  if omitted the server will use the default value of True
**points** | **[[float]]** | Specify multiple points for which the weight-, route-, time- or distance-matrix should be calculated as follows: &#x60;[longitude,latitude]&#x60;. In this case the origins are identical to the destinations. Thus, if there are N points, NxN entries are calculated. The order of the point parameter is important. Specify at least three points. Cannot be used together with &#x60;from_point&#x60; or &#x60;to_point.&#x60;. | [optional] 
**point_hints** | **[str]** | Optional parameter. Specifies a hint for each point in the &#x60;points&#x60; array to prefer a certain street for the closest location lookup. E.g. if there is an address or house with two or more neighboring streets you can control for which street the closest location is looked up. | [optional] 
**curbsides** | **[str]** | Optional parameter. It specifies on which side a point should be relative to the driver when she leaves/arrives at a start/target/via point. You need to specify this parameter for either none or all points. Only supported for motor vehicles and OpenStreetMap. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


