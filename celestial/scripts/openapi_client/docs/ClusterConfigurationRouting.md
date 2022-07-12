# ClusterConfigurationRouting


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**profile** | **str** | Specifies the vehicle profile of this type. The profile is used to determine the network, speed and other physical attributes to use for routing the vehicle or pedestrian. See the section about [routing profiles](#section/Map-Data-and-Routing-Profiles) for more details and valid profile values. | [optional]  if omitted the server will use the default value of "car"
**cost_per_second** | **float** | Cost per second (travel time) | [optional] 
**cost_per_meter** | **float** | Cost per meter (travel distance) | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


