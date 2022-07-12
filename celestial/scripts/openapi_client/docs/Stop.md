# Stop


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**address** | [**Address**](Address.md) |  | [optional] 
**duration** | **int** | Specifies the duration of the pickup or delivery in seconds, e.g. how long it takes unload items at the customer site. | [optional]  if omitted the server will use the default value of 0
**preparation_time** | **int** | Specifies the preparation time in seconds. It can be used to model parking lot search time since if you have 3 identical locations in a row, it only falls due once. | [optional]  if omitted the server will use the default value of 0
**time_windows** | [**[TimeWindow]**](TimeWindow.md) | Specifies an array of time window objects (see time window object below). For example, if an item needs to be delivered between 7am and 10am then specify the array as follows: [ { \&quot;earliest\&quot;: 25200, \&quot;latest\&quot; : 32400 } ] (starting the day from 0 in seconds). | [optional] 
**group** | **str** | Group this stop belongs to. See the group relation and [this post](https://discuss.graphhopper.com/t/4040) on how to utilize this. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


