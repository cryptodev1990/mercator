# Address


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**location_id** | **str** | Specifies the id of the location. | 
**lon** | **float** | Longitude of location. | 
**lat** | **float** | Latitude of location. | 
**name** | **str** | Name of location. | [optional] 
**street_hint** | **str** | Optional parameter. Specifies a hint for each address to better snap the coordinates (lon,lat) to road network. E.g. if there is an address or house with two or more neighboring streets you can control for which street the closest location is looked up. | [optional] 
**curbside** | **str** | Optional parameter. Specifies on which side a point should be relative to the driver when she leaves/arrives at a start/target/via point. Only supported for motor vehicles and OpenStreetMap. | [optional]  if omitted the server will use the default value of "any"
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


