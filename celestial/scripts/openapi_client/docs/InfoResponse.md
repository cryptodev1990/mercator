# InfoResponse

Information about the server and the geographical area that it covers.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**version** | **str** | The version of the GraphHopper server that provided this response. This is not related to the API version.  | [optional] 
**bbox** | **str** | The bounding box of the geographical area covered by this GraphHopper instance. Format: &#x60;\&quot;minLon,minLat,maxLon,maxLat\&quot;  | [optional] 
**features** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}** | The supported features, such as elevation, per vehicle profile.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


