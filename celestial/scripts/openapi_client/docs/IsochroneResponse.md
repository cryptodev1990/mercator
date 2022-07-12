# IsochroneResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**polygons** | [**[IsochroneResponsePolygon]**](IsochroneResponsePolygon.md) | The list of polygons in GeoJson format. It can be used e.g. in the Leaflet framework:  &#x60;&#x60;&#x60; L.geoJson(json.polygons).addTo(map) &#x60;&#x60;&#x60;  The number of polygon is identical to the specified buckets in the query. Every polygon contains the bucket number in the properties section of the GeoJson.  | [optional] 
**copyrights** | **[str]** |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


