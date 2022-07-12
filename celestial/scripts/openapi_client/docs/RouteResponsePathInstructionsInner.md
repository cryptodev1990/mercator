# RouteResponsePathInstructionsInner


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text** | **str** | A description what the user has to do in order to follow the route. The language depends on the locale parameter.  | [optional] 
**street_name** | **str** | The name of the street to turn onto in order to follow the route.  | [optional] 
**distance** | **float** | The distance for this instruction, in meters.  | [optional] 
**time** | **int** | The duration for this instruction, in milliseconds.  | [optional] 
**interval** | **[int]** | Two indices into &#x60;points&#x60;, referring to the beginning and the end of the segment of the route this instruction refers to.  | [optional] 
**sign** | **int** | A number which specifies the sign to show:  | sign | description  | |---|---| |-98| an U-turn without the knowledge if it is a right or left U-turn | | -8| a left U-turn | | -7| keep left | | -6| **not yet used**: leave roundabout | | -3| turn sharp left | | -2| turn left | | -1| turn slight left | |  0| continue on street | |  1| turn slight right | |  2| turn right | |  3| turn sharp right | |  4| the finish instruction before the last point | |  5| the instruction before a via point | |  6| the instruction before entering a roundabout | |  7| keep right | |  8| a right U-turn | |  *| **For future compatibility** it is important that all clients are able to handle also unknown instruction sign numbers  | [optional] 
**exit_number** | **int** | Only available for roundabout instructions (sign is 6). The count of exits at which the route leaves the roundabout.  | [optional] 
**turn_angle** | **float** | Only available for roundabout instructions (sign is 6). The radian of the route within the roundabout &#x60;0 &lt; r &lt; 2*PI&#x60; for clockwise and &#x60;-2*PI &lt; r &lt; 0&#x60; for counterclockwise turns.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


