# CustomModel

The custom_model modifies the routing behaviour of the specified profile. See the [detailed documentation](#section/Custom-Model).  Below is a complete request example in Berlin including the required `\"ch.disabled\": true` parameter.  ```json {   \"points\": [     [       13.31543,       52.509535     ],     [       13.29779,       52.512434     ]   ],   \"profile\": \"car\",   \"ch.disable\": true,   \"custom_model\": {     \"speed\": [       {         \"if\": \"true\",         \"limit_to\": 100       }     ],     \"priority\": [       {         \"if\": \"road_class == MOTORWAY\",         \"multiply_by\": 0       }     ],     \"distance_influence\": 100   } }  ``` 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**speed** | **[{str: (bool, date, datetime, dict, float, int, list, str, none_type)}]** | See [speed customization](#section/Custom-Model/Customizing-speed) | [optional] 
**priority** | **[{str: (bool, date, datetime, dict, float, int, list, str, none_type)}]** | See [priority customization](#section/Custom-Model/Customizing-priority) | [optional] 
**distance_influence** | **float** | Use higher values to prefer shorter routes. See [here](#section/Custom-Model/Customizing-distance_influence) for more details. | [optional]  if omitted the server will use the default value of 70
**areas** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}** | Areas are given in a GeoJson format. Currently only one format is supported: one object with type Feature, a geometry with type Polygon and optional (but ignored) id and properties fields. See more details and an example [here](#section/Custom-Model/Define-areas).  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


