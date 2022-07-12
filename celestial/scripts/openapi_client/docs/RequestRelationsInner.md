# RequestRelationsInner


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**vehicle_id** | **str** | Id of pre-assigned vehicle, i.e. the vehicle id that is determined to conduct the services and shipments in this relation. | [optional] 
**type** | **str** | Specifies the type of relation. It must be either of type &#x60;in_sequence&#x60;, &#x60;in_direct_sequence&#x60; or &#x60;neighbor&#x60;.  | [optional] 
**ids** | **[str]** | Specifies an array of shipment and/or service ids that are in relation. If you deal with services then you need to use the id of your services in ids. To also consider sequences of the pickups and deliveries of your shipments, you need to use a special ID, i.e. use your shipment id plus the keyword &#x60;_pickup&#x60; or &#x60;_delivery&#x60;. If you want to place a service or shipment activity at the beginning of your route, use the special ID &#x60;start&#x60;. In turn, use &#x60;end&#x60; to place it at the end of the route. | [optional] 
**groups** | **[str]** | An array of groups that should be related | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


