# Request


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**vehicles** | [**[Vehicle]**](Vehicle.md) | Specifies the available vehicles. | [optional] 
**vehicle_types** | [**[VehicleType]**](VehicleType.md) | Specifies the available vehicle types. These types can be assigned to vehicles. | [optional] 
**services** | [**[Service]**](Service.md) | Specifies the orders of the type \&quot;service\&quot;. These are, for example, pick-ups, deliveries or other stops that are to be approached by the specified vehicles. Each of these orders contains only one location. | [optional] 
**shipments** | [**[Shipment]**](Shipment.md) | Specifies the available shipments. Each shipment contains a pickup and a delivery stop, which must be processed one after the other. | [optional] 
**relations** | [**[RequestRelationsInner]**](RequestRelationsInner.md) | Defines additional relationships between orders. | [optional] 
**algorithm** | [**Algorithm**](Algorithm.md) |  | [optional] 
**objectives** | [**[Objective]**](Objective.md) | Specifies an objective function. The vehicle routing problem is solved in such a way that this objective function is minimized. | [optional] 
**cost_matrices** | [**[CostMatrix]**](CostMatrix.md) | Specifies your own tranport time and distance matrices. | [optional] 
**configuration** | [**Configuration**](Configuration.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


