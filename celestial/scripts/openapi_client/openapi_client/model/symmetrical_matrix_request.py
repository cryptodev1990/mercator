"""
    GraphHopper Directions API

     With the [GraphHopper Directions API](https://www.graphhopper.com/products/) you can integrate A-to-B route planning, turn-by-turn navigation, route optimization, isochrone calculations and other tools in your application.  The GraphHopper Directions API consists of the following RESTful web services:   * [Routing API](#tag/Routing-API),  * [Route Optimization API](#tag/Route-Optimization-API),  * [Isochrone API](#tag/Isochrone-API),  * [Map Matching API](#tag/Map-Matching-API),  * [Matrix API](#tag/Matrix-API),  * [Geocoding API](#tag/Geocoding-API) and  * [Cluster API](#tag/Cluster-API).  # Explore our APIs  ## Get started  1. [Sign up for GraphHopper](https://support.graphhopper.com/a/solutions/articles/44001976025) 2. [Create an API key](https://support.graphhopper.com/a/solutions/articles/44001976027)  Each API part has its own documentation. Jump to the desired API part and learn about the API through the given examples and tutorials.  In addition, for each API there are specific sample requests that you can send via Insomnia or Postman to see what the requests and responses look like.  ## Postman  To explore our APIs with [Postman](https://www.getpostman.com/), follow these steps:  1. Import our [request collections](https://gist.githubusercontent.com/oblonski/4b6ad76ba473eba049ae13f6230ea06a/raw/9a0bdf6f36a19f094f2a72eb22a03abb65851c07/graphhopper_directions_api.postman_collection.json) as well as our [environment file](https://gist.githubusercontent.com/oblonski/809b91874c4c5d1fd8a7ff68efb5b351/raw/261f427cb9b9702508670b73b06dd5350d30f373/graphhopper_directions_api.postman_environment.json). 2. Specify [your API key](https://graphhopper.com/dashboard/#/register) in your environment: `\"api_key\": your API key` 3. Start exploring  ![Postman](./img/postman.png)  ## API Client Libraries  To speed up development and make coding easier, we offer the following client libraries:   * [JavaScript client](https://github.com/graphhopper/directions-api-js-client) - try the [live examples](https://graphhopper.com/api/1/examples/)  * [Others](https://github.com/graphhopper/directions-api-clients) like C#, Ruby, PHP, Python, ... automatically created for the Route Optimization API  ### Bandwidth reduction  If you create your own client, make sure it supports http/2 and gzipped responses for best speed.  If you use the Matrix, the Route Optimization API or the Cluster API and want to solve large problems, we recommend you to reduce bandwidth by [compressing your POST request](https://gist.github.com/karussell/82851e303ea7b3459b2dea01f18949f4) and specifying the header as follows: `Content-Encoding: gzip`. This will also avoid the HTTP 413 error \"Request Entity Too Large\".  ## Contact Us  If you have problems or questions, please read the following information:  - [FAQ](https://graphhopper.com/api/1/docs/FAQ/) - [Public forum](https://discuss.graphhopper.com/c/directions-api) - [Contact us](https://www.graphhopper.com/contact-form/) - [GraphHopper Status Page](https://status.graphhopper.com/)  To stay informed about the latest developments, you can  - follow us on [twitter](https://twitter.com/graphhopper/), - read [our blog](https://graphhopper.com/blog/), - sign up for our newsletter or - [our forum](https://discuss.graphhopper.com/c/directions-api).  Select the channel you like the most.   # Map Data and Routing Profiles  Currently, our main data source is [OpenStreetMap](https://www.openstreetmap.org). We also integrated other network data providers. This chapter gives an overview about the options you have.  ## OpenStreetMap  #### Geographical Coverage  [OpenStreetMap](https://www.openstreetmap.org) covers the whole world. If you want to see for yourself if we can provide data suitable for your region, please visit [GraphHopper Maps](https://graphhopper.com/maps/). You can edit and modify OpenStreetMap data if you find that important information is missing, e.g. a weight limit for a bridge. [Here](https://wiki.openstreetmap.org/wiki/Beginners%27_guide) is a beginner's guide that shows how to add data. If you have edited data, we usually consider your data after 1 week at the latest.  #### Supported Routing Profiles  The Routing, Matrix and Route Optimization APIs support the following profiles:  Name             | Description           | Restrictions                        | Icon -----------------|:----------------------|:------------------------------------|:--------------------------------------------------------- car              | Car mode              | car access, weight=2500kg, width=2m, height=2m           | ![car image](https://graphhopper.com/maps/img/car.png) car_delivery     | Car mode              | car access including delivery and private roads | ![car image](https://graphhopper.com/maps/img/car.png) car_avoid_ferry      | Car mode          | car that heavily penalizes ferries          | ![car image](https://graphhopper.com/maps/img/car.png) car_avoid_motorway   | Car mode          | car that heavily penalizes motorways        | ![car image](https://graphhopper.com/maps/img/car.png) car_avoid_toll       | Car mode          | car that heavily penalizes tolls            | ![car image](https://graphhopper.com/maps/img/car.png) small_truck          | Small truck like a Mercedes Sprinter, Ford Transit or Iveco Daily | height=2.7m, width=2+0.34m, length=5.5m, weight=2080+1400 kg | ![small truck image](https://graphhopper.com/maps/img/small_truck.png) small_truck_delivery | Small truck                                             | like small_truck but including delivery and private roads             | ![small truck image](https://graphhopper.com/maps/img/small_truck.png) truck                  | Truck like a MAN or Mercedes-Benz Actros              | height=3.7m, width=2.6+0.34m, length=12m, weight=13000+13000 kg, hgv=yes, 3 Axes | ![truck image](https://graphhopper.com/maps/img/truck.png) scooter                | Moped mode | Fast inner city, often used for food delivery, is able to ignore certain bollards, maximum speed of roughly 50km/h. weight=300kg, width=1m, height=2m | ![scooter image](https://graphhopper.com/maps/img/scooter.png) scooter_delivery       | Moped mode | Like scooter but including delivery and private roads | ![scooter image](https://graphhopper.com/maps/img/scooter.png)     foot       | Pedestrian or walking without dangerous [SAC-scales](https://wiki.openstreetmap.org/wiki/Key:sac_scale) | foot access         | ![foot image](https://graphhopper.com/maps/img/foot.png) hike       | Pedestrian or walking with priority for more beautiful hiking tours and potentially a bit longer than `foot`. Walking duration is influenced by elevation differences.  | foot access         | ![hike image](https://graphhopper.com/maps/img/hike.png) bike       | Trekking bike avoiding hills | bike access         | ![Bike image](https://graphhopper.com/maps/img/bike.png) mtb        | Mountainbike                 | bike access         | ![Mountainbike image](https://graphhopper.com/maps/img/mtb.png) racingbike | Bike preferring roads        | bike access         | ![Racingbike image](https://graphhopper.com/maps/img/racingbike.png)  Please note:   * the free package supports only the routing profiles `car`, `bike` or `foot`  * up to 2 different routing profiles can be used in a single request towards the Route Optimization API. The number of vehicles is unaffected and depends on your subscription.  * we offer custom routing profiles with different properties, different speed profiles or different access options. To find out more about custom profiles, please [contact us](https://www.graphhopper.com/contact-form/).  * a sophisticated `motorcycle` profile is available up on request. It is powered by the [Kurviger](https://kurviger.de/en) Routing API and favors curves and slopes while avoiding cities and highways.   ## TomTom  If you want to include traffic, you can purchase the TomTom Add-on. This Add-on only uses TomTom's road network and historical traffic information. Live traffic is not yet considered. If you are interested to learn how we consider traffic information, we recommend that you read [this article](https://www.graphhopper.com/blog/2017/11/06/time-dependent-optimization/).  Please note the following:   * Currently we only offer this for our [Route Optimization API](#tag/Route-Optimization-API). [Contact us](https://www.graphhopper.com/contact-form/) if you would like to use it for the Matrix or Routing API.  * In addition to our terms, you need to accept TomTom's [End User License Aggreement](https://www.graphhopper.com/tomtom-end-user-license-agreement/).  * We do *not* use TomTom's web services. We only use their data with our software.   [Contact us](https://www.graphhopper.com/contact-form/) if you want to buy this TomTom add-on.  #### Geographical Coverage  We offer  - Europe including Russia - North, Central and South America - Saudi Arabia and United Arab Emirates - South Africa - Southeast Asia - Australia  #### Supported Vehicle Profiles  Name       | Description           | Restrictions              | Icon -----------|:----------------------|:--------------------------|:--------------------------------------------------------- car        | Car mode              | car access                | ![car image](https://graphhopper.com/maps/img/car.png) small_truck| Small truck like a Mercedes Sprinter, Ford Transit or Iveco Daily | height=2.7m, width=2+0.4m, length=5.5m, weight=2080+1400 kg | ![small truck image](https://graphhopper.com/maps/img/small_truck.png)    # Custom Model  A custom model allows you to modify the default routing behavior of a vehicle profile by specifying a set of rules in JSON language. There are three JSON properties to change a profile: `priority`, `speed` and `distance_influence` that are described in great detail in the next sections.  But first we will give an introductory example for each of these JSON properties. Let's start with `speed`:  ```json {   \"speed\": [{     \"if\": \"road_class == MOTORWAY\",     \"limit_to\": 90   }] } ```  As you might have already guessed this limits the speed on motorways to 90km/h. Changing the speed will of course change the travel time, but at the same time this makes other road classes more likely as well, so you can use this model to avoid motorways.  You can immediately try this out in the Browser [on GraphHopper Maps](https://graphhopper.com/maps/?point=50.856527%2C12.876127&point=51.02952%2C13.295603&profile=car&custom_model=%7B%22speed%22%3A%5B%7B%22if%22%3A%22road_class+=%3D+MOTORWAY%22%2C%22limit_to%22%3A90%7D%5D%7D). GraphHopper Maps offers an interactive text editor to comfortably enter custom models. You can open it by pressing the \"custom\" button. It will check the syntax of your custom model and mark errors in red. You can press Ctrl+Space or Alt+Enter to retrieve auto-complete suggestions. Pressing Ctrl+Enter will send a routing request for the custom model you entered. To disable the custom model you click the \"custom\" button again.   In the second example we show how to avoid certain road classes without changing the travel time:  ```json {   \"priority\": [{     \"if\": \"road_class == LIVING_STREET || road_class == RESIDENTIAL || road_class == UNCLASSIFIED\",     \"multiply_by\": 0.1   }] } ```  This example avoids certain smaller streets. [View it in GraphHopper Maps](https://graphhopper.com/maps/?point=51.125708%2C13.067915&point=51.125964%2C13.082271&profile=car&custom_model=%7B%22priority%22%3A%5B%7B%22if%22%3A%22road_class+=%3D+LIVING_STREET+%7C%7C+road_class+%3D%3D+RESIDENTIAL+%7C%7C+road_class+%3D%3D+UNCLASSIFIED%22%2C%22multiply_by%22%3A0.1%7D%5D%7D).  The third example shows how to prefer shortest paths:  ```json {   \"distance_influence\": 200 } ```  [View this example in GraphHopper Maps](https://graphhopper.com/maps/?point=51.04188%2C13.057766&point=51.057527%2C13.068237&profile=car&custom_model=%7B%22distance_influence%22%3A200%7D).  There is a fourth JSON property `areas` that allows you to define areas that can then be used in the `if` or `else_if` conditions for `speed` and `priority`. Please read more about this and the other properties below and try some examples in [GraphHopper Maps](https://graphhopper.com/maps/) with the help of [this blog post](https://www.graphhopper.com/blog/2020/05/31/examples-for-customizable-routing/).   ## Customizing speed  When using custom models you do not need to define rules that specify a speed for every road segment, but rather GraphHopper assumes a default speed. All you need to do is adjust this default speed to your use-case as you will always use the custom  model in conjunction with a routing profile which is used to determine the default speed.  The custom model is a JSON object and the first property we will learn about here is the `speed` property. The `speed` property's value is a list of conditional statements that modify the default speed. Every such statement consists of a condition and an operation. The different statements are applied to the default speed from top to bottom, i.e. statements that come later in the list are applied to the resulting value of previous operations. Each statement is only executed if the corresponding condition applies for the current road segment. This will become more clear in the following examples.  Currently the custom model language supports two operators:  - `multiply_by` multiplies the speed value with a given number - `limit_to` limits the speed value to a given number  #### `if` statements and the `multiply_by` operation  Let's start with a simple example using `multiply_by`:  ```json {   \"speed\": [     {       \"if\": \"road_class == MOTORWAY\",       \"multiply_by\": 0.5     }   ] } ```  This custom model reduces the speed of every road segment for which the `road_class` attribute is `MOTORWAY` to fifty percent of the default speed (the default speed is multiplied by `0.5`). Again, the default speed is the speed that GraphHopper would normally use for the profile's vehicle. Note the `if` clause which means that the operation (`multiply_by`) is only applied *if* the condition `road_class == MOTORWAY` is fulfilled for the road segment under consideration. The `==` indicates equality, i.e. the condition reads \"the road_class equals MOTORWAY\". If you're a bit familiar with programming note that the condition (the value of the `if` key) is just a boolean condition in Java language (other programming languages like C or JavaScript are very similar in this regard). A more complex condition could look like this: `road_class == PRIMARY || road_class == TERTIARY` which uses the **or** (`||`) operator and literally means \"road_class equals PRIMARY or road_class equals TERTIARY\".  There can be multiple such 'if statements' in the speed section, and they are evaluated from top to bottom:  ```json {   \"speed\": [     {       \"if\": \"road_class == MOTORWAY\",       \"multiply_by\": 0.5     },     {       \"if\": \"road_class == PRIMARY || road_environment == TUNNEL\",       \"multiply_by\": 0.7     }   ] } ```  In this example the default speed of road segments with `road_class == MOTORWAY` will be multiplied by `0.5`, the default speed of road segments with `road_class == PRIMARY` will be multiplied by `0.7` and for road segments with both `road_class == MOTORWAY` and `road_environment == TUNNEL` the default speed will be multiplied first by `0.5` and then by `0.7`. So overall the default speed will be multiplied by `0.35`. For road segments with `road_class == PRIMARY` and `road_environment == TUNNEL` we only multiply by `0.7`, even though both parts of the second condition apply. It only matters whether the road segment matches the condition or not.  `road_class` and `road_environment` are road attributes of 'enum' type, i.e. their value can only be one of a fixed set of values, like `MOTORWAY` for `road_class`.  Other road attributes like `get_off_bike` are of `boolean` type. They can be used as conditions directly, for example:  ```json {   \"speed\": [     {       \"if\": \"get_off_bike\",       \"multiply_by\": 0.6     }   ] } ```  which means that for road segments with `get_off_bike==true` the speed factor will be `0.6`.  For attributes with numeric values, like `max_width` you should not use the `==` (equality) or `!=` ( inequality) operators, but the numerical comparison operators \"bigger\" `>`, \"bigger or equals\" `>=`, \"smaller\" `<`, or \"smaller or equals\" `<=`, e.g.:  ```json {   \"speed\": [     {       \"if\": \"max_width < 2.5\",       \"multiply_by\": 0.8     }   ] } ```   which means that for all road segments with `max_width` smaller than `2.5m` the speed is multiplied by `0.8`.   ### The `limit_to` operation  Besides the `multiply_by` operator there is also the `limit_to` operator. As the name suggests `limit_to` limits the current value to the given value. Take this example:  ```json {   \"speed\": [     {       \"if\": \"road_class == MOTORWAY\",       \"multiply_by\": 0.8     },     {       \"if\": \"surface == GRAVEL\",       \"limit_to\": 60     }   ] } ```  This implies that on all road segments with the `GRAVEL` value for `surface` the speed will be at most `60km/h`, regardless of the default speed and the previous rules. So for a road segment with `road_class == MOTORWAY`, `surface == GRAVEL` and default speed `100` the first statement reduces the speed from `100` to `80` and the second statement further reduces the speed from `80` to `60`. If the `road_class` was `PRIMARY` and the default speed was `50` the first rule would not apply and the second rule would do nothing, because limiting `50` to `60` still yields `50`.  Note that all values used for `limit_to` must be in the range `[0, max_vehicle_speed]` where `max_vehicle_speed` is the maximum speed that is set for the base vehicle and cannot be changed.  A common use-case for the `limit_to` operation is the following pattern:  ```json {   \"speed\": [     {       \"if\": \"true\",       \"limit_to\": 90     }   ] } ```  which means that the speed is limited to `90km/h` for all road segments regardless of its properties. The condition \"`true`\" is always fulfilled.  ### `else` and `else_if` statements  The `else` statement allows you to define that some operations should be applied if an road segment does **not** match a condition. So this example:  ```json {   \"speed\": [     {       \"if\": \"road_class == MOTORWAY\",       \"multiply_by\": 0.5     },     {       \"else\": \"\",       \"limit_to\": 50     }   ] } ```  means that for all road segments with `road_class == MOTORWAY` we multiply the default speed by `0.5` and for all others we limit the default speed to `50` (but never both).  In case you want to distinguish more than two cases (road segments that match or match not a condition) you can use `else_if` statements which are only evaluated in case the previous `if` or `else_if` statement did **not** match:  ```json {   \"speed\": [     {       \"if\": \"road_class == MOTORWAY\",       \"multiply_by\": 0.5     },     {       \"else_if\": \"road_environment == TUNNEL\",       \"limit_to\": 70     },     {       \"else\": \"\",       \"multiply_by\": 0.9     }   ] } ```  So if the first condition matches (`road_class == MOTORWAY`) the default speed is multiplied by `0.5`, but the other two statements are ignored. Only if the first statement does not match (e.g. `road_class == PRIMARY`) the second statement is even considered and only if it matches (`road_environment == TUNNEL`) the default speed is limited to 70. The last operation (`multiply_by: 0.9`) is only applied if both previous conditions did not match.  `else` and `else_if` statements always require a preceding `if` or `else_if` statement. However, there can be multiple 'blocks' of subsequent `if/else_if/else` statements in the list of rules for `speed`.  `else_if` is useful for example in case you have multiple `multiply_by` operations, but you do not want that the speed gets reduced by all of them. For the following model  ```json {   \"speed\": [     {       \"if\": \"road_class == MOTORWAY\",       \"multiply_by\": 0.5     },     {       \"else_if\": \"road_environment == TUNNEL\",       \"multiply_by\": 0.8     }   ] } ```  only the first factor (`0.5`) will be applied even for road segments that fulfill both conditions.  ## Limit rules to certain areas  You can not only modify the speed of road segments based on properties, like we saw in the previous examples, but you can also modify the speed of road segments based on their location. To do this you need to first create and add some areas to the `areas` section of the custom model. You can then use the name of these areas in the conditions of your `if/else/else_if` statements.  In the following example we multiply the speed of all road segments in an area called `custom1` with `0.7` and also limit it to `50km/h`. Note that each area's name needs to be prefixed with `in_`:  ```json {   \"speed\": [     {       \"if\": \"in_custom1\",       \"multiply_by\": 0.7     },     {       \"if\": \"in_custom1\",       \"limit_to\": 50     }   ],   \"areas\": {     \"custom1\": {       \"type\": \"Feature\",       \"id\": \"something\",       \"properties\": {},       \"geometry\": {         \"type\": \"Polygon\",         \"coordinates\": [           [             [               1.525,               42.511             ],             [               1.510,               42.503             ],             [               1.531,               42.495             ],             [               1.542,               42.505             ],             [               1.525,               42.511             ]           ]         ]       }     }   } } ```  Areas are given in GeoJson format, but currently only the exact format in the above example is supported, i.e. one object with type `Feature`, a geometry with type `Polygon` and optional (but ignored) `id` and `properties` fields. Note that the coordinates array of `Polygon` is an array of arrays that each must describe a closed ring, i.e. the first point must be equal to the last. Each point is given as an array [longitude, latitude], so the coordinates array has three dimensions total.  Using the `areas` feature you can also block entire areas i.e. by multiplying the speed with `0`, but for this you should rather use the `priority` section that we will explain next.  ## Customizing priority  Make sure you read the introductory section of this document to learn what the `priority` factor means. In short it allows similar modifications as `speed`, but instead of modifying the road segment weights *and* travel times it will only affect the weights. By default, the priority is `1` for every road segment, so it does not affect the weight. However, changing the priority of a road can yield a relative weight difference in comparison to other roads.  Customizing the `priority` works very much like changing the `speed`, so in case you did not read the section about `speed` you should go back there and read it now. The only real difference is that there is no `limit_to` operator for `priority`. As a quick reminder here is an example for priority:  ```json {   \"priority\": [     {       \"if\": \"road_class == MOTORWAY\",       \"multiply_by\": 0.5     },     {       \"else_if\": \"road_class == SECONDARY\",       \"multiply_by\": 0.9     },     {       \"if\": \"road_environment == TUNNEL\",       \"multiply_by\": 0.1     }   ] } ```  means that road segments with `road_class==MOTORWAY` and `road_environment==TUNNEL` get priority `0.5*0.1=0.05` and those with `road_class==SECONDARY` and no TUNNEL, get priority `0.9` and so on.  Edges with lower priority values will be less likely part of the optimal route calculated by GraphHopper, higher values mean that these road segments shall be preferred. If you do not want to state which road segments shall be avoided, but rather which ones shall be preferred, you need to **decrease** the priority of others:  ```json {   \"priority\": [     {       \"if\": \"road_class != CYCLEWAY\",       \"multiply_by\": 0.8     }   ] } ```  means decreasing the priority for all road_classes *except* cycleways.  Just like we saw for `speed` you can also adjust the priority for road segments in a certain area. It works exactly the same way:  ```json {   \"priority\": [     {       \"if\": \"in_custom1\",       \"multiply_by\": 0.7     }   ] } ```  To block an entire area set the priority value to `0`. You can even set the priority only for certain roads in an area like this:  ```json {   \"priority\": [     {       \"if\": \"road_class == MOTORWAY && in_custom1\",       \"multiply_by\": 0.1     }   ] } ```  Some other useful attributes to restrict access to certain roads depending on your vehicle dimensions are the following:  ```json {   \"priority\": [     {       \"if\": \"max_width < 2.5\",       \"multiply_by\": 0     },     {       \"if\": \"max_length < 10\",       \"multiply_by\": 0     },     {       \"if\": \"max_weight < 3.5\",       \"multiply_by\": 0     }   ] } ```  which means that the priority for all road segments that allow a maximum vehicle width of `2.5m`, a maximum vehicle length of `10m` or a maximum vehicle weight of `3.5tons`, or less, is zero, i.e. these \"narrow\" road segments are blocked.  ## Customizing distance_influence  The `distance_influence` property allows you to control the trade-off between a fast route (minimum time) and a short route (minimum distance). The larger `distance_influence` is the more GraphHopper will prioritize routes with a small total distance. More precisely, the `distance_influence` is the time you need to save on a detour (a longer distance route option) such that you prefer taking the detour compared to a shorter route.   A value of `100` means that one extra kilometer of detour must save you `100s` of travelling time or else you are not  willing to take the detour. Or to put it another way, if a reference route takes `600s` and is `10km` long,  `distance_influence=100` means that you are willing to take an alternative route that is `11km` long only if  it takes no longer than `500s` (saves `100s`). Things get a bit more complicated when `priority` is not `1`, but the  effect stays the same: The larger `distance_influence` is, the more GraphHopper will focus on finding short routes.   ## Road attributes  GraphHopper stores different attributes for every road segment. Some frequently used are the following (some of their possible values are given in brackets):  - road_class: (OTHER, MOTORWAY, TRUNK, PRIMARY, SECONDARY, TRACK, STEPS, CYCLEWAY, FOOTWAY, ...) - road_environment: (ROAD, FERRY, BRIDGE, TUNNEL, ...) - road_access: (DESTINATION, DELIVERY, PRIVATE, NO, ...) - surface: (PAVED, DIRT, SAND, GRAVEL, ...) - smoothness: (EXCELLENT, GOOD, INTERMEDIATE, ...) - toll: (NO, ALL, HGV)  To learn about all available attributes you can query the `/info` endpoint or use auto complete in GraphHopper Maps.  Besides these road attributes, which can take distinct string values, there are also some that represent a boolean value (they are either true or false for a given road segment), like:  - get_off_bike - road_class_link  There are also some that take on a numeric value, like:  - max_weight - max_height - max_width  ## Limitations  Custom models are currently:  1. only available for the [POST Route Endpoint](#operation/postRoute). If you are interested in using this for the Matrix or Route Optimization API please [contact us](https://www.graphhopper.com/contact-form/) to get access to an early alpha version. For the Isochrone API it is also planned. 2. only available for the following parent profiles: `foot`, `bike`, `scooter`, `car` and `small_truck`. 3. only available for OpenStreetMap.  This feature will strongly benefit from feedback, so do not hesitate to share your experience, your favorite custom model or some of the problems you ran into when you tried building your own with custom model.  ## Troubleshooting  ### Recommendations  For debugging you can use the custom model editor in [GraphHopper Maps](https://graphhopper.com/maps/) (click the 'custom' button).  When debugging problems with custom models you should first try if your request goes through without an error using an empty custom model.  For production you should avoid to include road_access and toll in the profile as we will change their values in the next weeks which could cause unexpected problems.  ### All routes for my custom model fail  This could mean that either your custom model made some of the roads near the start and destination inaccessible,  then usually we return a PointNotFoundException with the point_index with the \"location snap\" problem.  Or, the custom model made all roads between your start and destination inaccessible, then we return a ConnectionNotFoundException. This happens e.g. when you exclude tunnels,  ferries or motorways but all routes between start and destination have these road attributes satisfied, i.e. we cannot find a route.  **Solution**: relax your custom model and e.g. instead of excluding certain road attributes via `\"multiply_by\": 0` you should try to use `0.01`.   # noqa: E501

    The version of the OpenAPI document: 1.0.0
    Contact: support@graphhopper.com
    Generated by: https://openapi-generator.tech
"""


import re  # noqa: F401
import sys  # noqa: F401

from openapi_client.model_utils import (  # noqa: F401
    ApiTypeError,
    ModelComposed,
    ModelNormal,
    ModelSimple,
    cached_property,
    change_keys_js_to_python,
    convert_js_args_to_python_args,
    date,
    datetime,
    file_type,
    none_type,
    validate_get_composed_info,
    OpenApiModel
)
from openapi_client.exceptions import ApiAttributeError



class SymmetricalMatrixRequest(ModelNormal):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.

    Attributes:
      allowed_values (dict): The key is the tuple path to the attribute
          and the for var_name this is (var_name,). The value is a dict
          with a capitalized key describing the allowed value and an allowed
          value. These dicts store the allowed enum values.
      attribute_map (dict): The key is attribute name
          and the value is json key in definition.
      discriminator_value_class_map (dict): A dict to go from the discriminator
          variable value to the discriminator class name.
      validations (dict): The key is the tuple path to the attribute
          and the for var_name this is (var_name,). The value is a dict
          that stores validations for max_length, min_length, max_items,
          min_items, exclusive_maximum, inclusive_maximum, exclusive_minimum,
          inclusive_minimum, and regex.
      additional_properties_type (tuple): A tuple of classes accepted
          as additional properties values.
    """

    allowed_values = {
    }

    validations = {
    }

    @cached_property
    def additional_properties_type():
        """
        This must be a method because a model may have properties that are
        of type self, this must run after the class is loaded
        """
        return (bool, date, datetime, dict, float, int, list, str, none_type,)  # noqa: E501

    _nullable = False

    @cached_property
    def openapi_types():
        """
        This must be a method because a model may have properties that are
        of type self, this must run after the class is loaded

        Returns
            openapi_types (dict): The key is attribute name
                and the value is attribute type.
        """
        return {
            'profile': (str,),  # noqa: E501
            'points': ([[float]],),  # noqa: E501
            'point_hints': ([str],),  # noqa: E501
            'snap_preventions': ([str],),  # noqa: E501
            'curbsides': ([str],),  # noqa: E501
            'out_arrays': ([str],),  # noqa: E501
            'fail_fast': (bool,),  # noqa: E501
        }

    @cached_property
    def discriminator():
        return None


    attribute_map = {
        'profile': 'profile',  # noqa: E501
        'points': 'points',  # noqa: E501
        'point_hints': 'point_hints',  # noqa: E501
        'snap_preventions': 'snap_preventions',  # noqa: E501
        'curbsides': 'curbsides',  # noqa: E501
        'out_arrays': 'out_arrays',  # noqa: E501
        'fail_fast': 'fail_fast',  # noqa: E501
    }

    read_only_vars = {
    }

    _composed_schemas = {}

    @classmethod
    @convert_js_args_to_python_args
    def _from_openapi_data(cls, *args, **kwargs):  # noqa: E501
        """SymmetricalMatrixRequest - a model defined in OpenAPI

        Keyword Args:
            _check_type (bool): if True, values for parameters in openapi_types
                                will be type checked and a TypeError will be
                                raised if the wrong type is input.
                                Defaults to True
            _path_to_item (tuple/list): This is a list of keys or values to
                                drill down to the model in received_data
                                when deserializing a response
            _spec_property_naming (bool): True if the variable names in the input data
                                are serialized names, as specified in the OpenAPI document.
                                False if the variable names in the input data
                                are pythonic names, e.g. snake case (default)
            _configuration (Configuration): the instance to use when
                                deserializing a file_type parameter.
                                If passed, type conversion is attempted
                                If omitted no type conversion is done.
            _visited_composed_classes (tuple): This stores a tuple of
                                classes that we have traveled through so that
                                if we see that class again we will not use its
                                discriminator again.
                                When traveling through a discriminator, the
                                composed schema that is
                                is traveled through is added to this set.
                                For example if Animal has a discriminator
                                petType and we pass in "Dog", and the class Dog
                                allOf includes Animal, we move through Animal
                                once using the discriminator, and pick Dog.
                                Then in Dog, we will make an instance of the
                                Animal class but this time we won't travel
                                through its discriminator because we passed in
                                _visited_composed_classes = (Animal,)
            profile (str): Specifies the vehicle profile of this type. The profile is used to determine the network, speed and other physical attributes to use for routing the vehicle or pedestrian. See the section about [routing profiles](#section/Map-Data-and-Routing-Profiles) for more details and valid profile values.. [optional] if omitted the server will use the default value of "car"  # noqa: E501
            points ([[float]]): Specify multiple points for which the weight-, route-, time- or distance-matrix should be calculated as follows: `[longitude,latitude]`. In this case the origins are identical to the destinations. Thus, if there are N points, NxN entries are calculated. The order of the point parameter is important. Specify at least three points. Cannot be used together with `from_point` or `to_point.`.. [optional]  # noqa: E501
            point_hints ([str]): Optional parameter. Specifies a hint for each point in the `points` array to prefer a certain street for the closest location lookup. E.g. if there is an address or house with two or more neighboring streets you can control for which street the closest location is looked up.. [optional]  # noqa: E501
            snap_preventions ([str]): Optional parameter to avoid snapping to a certain road class or road environment. Current supported values `motorway`, `trunk`, `ferry`, `tunnel`, `bridge` and `ford`. Please note that this feature does not e.g. avoid motorways for the route - it only avoids it for the \"location snap\".. [optional]  # noqa: E501
            curbsides ([str]): Optional parameter. It specifies on which side a point should be relative to the driver when she leaves/arrives at a start/target/via point. You need to specify this parameter for either none or all points. Only supported for motor vehicles and OpenStreetMap.. [optional]  # noqa: E501
            out_arrays ([str]): Specifies which matrices should be included in the response. Specify one or more of the following options `weights`, `times`, `distances`. The units of the entries of `distances` are meters, of `times` are seconds and of `weights` is arbitrary and it can differ for different vehicle profiles or versions of this API.. [optional]  # noqa: E501
            fail_fast (bool): Specifies whether or not the matrix calculation should return with an error as soon as possible in case some points cannot be found or some points are not connected. If set to `false` the time/weight/distance matrix will be calculated for all valid points and contain the `null` value for all entries that could not be calculated. The `hint` field of the response will also contain additional information about what went wrong (see its documentation).. [optional] if omitted the server will use the default value of True  # noqa: E501
        """

        _check_type = kwargs.pop('_check_type', True)
        _spec_property_naming = kwargs.pop('_spec_property_naming', True)
        _path_to_item = kwargs.pop('_path_to_item', ())
        _configuration = kwargs.pop('_configuration', None)
        _visited_composed_classes = kwargs.pop('_visited_composed_classes', ())

        self = super(OpenApiModel, cls).__new__(cls)

        if args:
            for arg in args:
                if isinstance(arg, dict):
                    kwargs.update(arg)
                else:
                    raise ApiTypeError(
                        "Invalid positional arguments=%s passed to %s. Remove those invalid positional arguments." % (
                            args,
                            self.__class__.__name__,
                        ),
                        path_to_item=_path_to_item,
                        valid_classes=(self.__class__,),
                    )

        self._data_store = {}
        self._check_type = _check_type
        self._spec_property_naming = _spec_property_naming
        self._path_to_item = _path_to_item
        self._configuration = _configuration
        self._visited_composed_classes = _visited_composed_classes + (self.__class__,)

        for var_name, var_value in kwargs.items():
            if var_name not in self.attribute_map and \
                        self._configuration is not None and \
                        self._configuration.discard_unknown_keys and \
                        self.additional_properties_type is None:
                # discard variable.
                continue
            setattr(self, var_name, var_value)
        return self

    required_properties = set([
        '_data_store',
        '_check_type',
        '_spec_property_naming',
        '_path_to_item',
        '_configuration',
        '_visited_composed_classes',
    ])

    @convert_js_args_to_python_args
    def __init__(self, *args, **kwargs):  # noqa: E501
        """SymmetricalMatrixRequest - a model defined in OpenAPI

        Keyword Args:
            _check_type (bool): if True, values for parameters in openapi_types
                                will be type checked and a TypeError will be
                                raised if the wrong type is input.
                                Defaults to True
            _path_to_item (tuple/list): This is a list of keys or values to
                                drill down to the model in received_data
                                when deserializing a response
            _spec_property_naming (bool): True if the variable names in the input data
                                are serialized names, as specified in the OpenAPI document.
                                False if the variable names in the input data
                                are pythonic names, e.g. snake case (default)
            _configuration (Configuration): the instance to use when
                                deserializing a file_type parameter.
                                If passed, type conversion is attempted
                                If omitted no type conversion is done.
            _visited_composed_classes (tuple): This stores a tuple of
                                classes that we have traveled through so that
                                if we see that class again we will not use its
                                discriminator again.
                                When traveling through a discriminator, the
                                composed schema that is
                                is traveled through is added to this set.
                                For example if Animal has a discriminator
                                petType and we pass in "Dog", and the class Dog
                                allOf includes Animal, we move through Animal
                                once using the discriminator, and pick Dog.
                                Then in Dog, we will make an instance of the
                                Animal class but this time we won't travel
                                through its discriminator because we passed in
                                _visited_composed_classes = (Animal,)
            profile (str): Specifies the vehicle profile of this type. The profile is used to determine the network, speed and other physical attributes to use for routing the vehicle or pedestrian. See the section about [routing profiles](#section/Map-Data-and-Routing-Profiles) for more details and valid profile values.. [optional] if omitted the server will use the default value of "car"  # noqa: E501
            points ([[float]]): Specify multiple points for which the weight-, route-, time- or distance-matrix should be calculated as follows: `[longitude,latitude]`. In this case the origins are identical to the destinations. Thus, if there are N points, NxN entries are calculated. The order of the point parameter is important. Specify at least three points. Cannot be used together with `from_point` or `to_point.`.. [optional]  # noqa: E501
            point_hints ([str]): Optional parameter. Specifies a hint for each point in the `points` array to prefer a certain street for the closest location lookup. E.g. if there is an address or house with two or more neighboring streets you can control for which street the closest location is looked up.. [optional]  # noqa: E501
            snap_preventions ([str]): Optional parameter to avoid snapping to a certain road class or road environment. Current supported values `motorway`, `trunk`, `ferry`, `tunnel`, `bridge` and `ford`. Please note that this feature does not e.g. avoid motorways for the route - it only avoids it for the \"location snap\".. [optional]  # noqa: E501
            curbsides ([str]): Optional parameter. It specifies on which side a point should be relative to the driver when she leaves/arrives at a start/target/via point. You need to specify this parameter for either none or all points. Only supported for motor vehicles and OpenStreetMap.. [optional]  # noqa: E501
            out_arrays ([str]): Specifies which matrices should be included in the response. Specify one or more of the following options `weights`, `times`, `distances`. The units of the entries of `distances` are meters, of `times` are seconds and of `weights` is arbitrary and it can differ for different vehicle profiles or versions of this API.. [optional]  # noqa: E501
            fail_fast (bool): Specifies whether or not the matrix calculation should return with an error as soon as possible in case some points cannot be found or some points are not connected. If set to `false` the time/weight/distance matrix will be calculated for all valid points and contain the `null` value for all entries that could not be calculated. The `hint` field of the response will also contain additional information about what went wrong (see its documentation).. [optional] if omitted the server will use the default value of True  # noqa: E501
        """

        _check_type = kwargs.pop('_check_type', True)
        _spec_property_naming = kwargs.pop('_spec_property_naming', False)
        _path_to_item = kwargs.pop('_path_to_item', ())
        _configuration = kwargs.pop('_configuration', None)
        _visited_composed_classes = kwargs.pop('_visited_composed_classes', ())

        if args:
            for arg in args:
                if isinstance(arg, dict):
                    kwargs.update(arg)
                else:
                    raise ApiTypeError(
                        "Invalid positional arguments=%s passed to %s. Remove those invalid positional arguments." % (
                            args,
                            self.__class__.__name__,
                        ),
                        path_to_item=_path_to_item,
                        valid_classes=(self.__class__,),
                    )

        self._data_store = {}
        self._check_type = _check_type
        self._spec_property_naming = _spec_property_naming
        self._path_to_item = _path_to_item
        self._configuration = _configuration
        self._visited_composed_classes = _visited_composed_classes + (self.__class__,)

        for var_name, var_value in kwargs.items():
            if var_name not in self.attribute_map and \
                        self._configuration is not None and \
                        self._configuration.discard_unknown_keys and \
                        self.additional_properties_type is None:
                # discard variable.
                continue
            setattr(self, var_name, var_value)
            if var_name in self.read_only_vars:
                raise ApiAttributeError(f"`{var_name}` is a read-only attribute. Use `from_openapi_data` to instantiate "
                                     f"class with read only attributes.")
