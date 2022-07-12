"""
    GraphHopper Directions API

     With the [GraphHopper Directions API](https://www.graphhopper.com/products/) you can integrate A-to-B route planning, turn-by-turn navigation, route optimization, isochrone calculations and other tools in your application.  The GraphHopper Directions API consists of the following RESTful web services:   * [Routing API](#tag/Routing-API),  * [Route Optimization API](#tag/Route-Optimization-API),  * [Isochrone API](#tag/Isochrone-API),  * [Map Matching API](#tag/Map-Matching-API),  * [Matrix API](#tag/Matrix-API),  * [Geocoding API](#tag/Geocoding-API) and  * [Cluster API](#tag/Cluster-API).  # Explore our APIs  ## Get started  1. [Sign up for GraphHopper](https://support.graphhopper.com/a/solutions/articles/44001976025) 2. [Create an API key](https://support.graphhopper.com/a/solutions/articles/44001976027)  Each API part has its own documentation. Jump to the desired API part and learn about the API through the given examples and tutorials.  In addition, for each API there are specific sample requests that you can send via Insomnia or Postman to see what the requests and responses look like.  ## Postman  To explore our APIs with [Postman](https://www.getpostman.com/), follow these steps:  1. Import our [request collections](https://gist.githubusercontent.com/oblonski/4b6ad76ba473eba049ae13f6230ea06a/raw/9a0bdf6f36a19f094f2a72eb22a03abb65851c07/graphhopper_directions_api.postman_collection.json) as well as our [environment file](https://gist.githubusercontent.com/oblonski/809b91874c4c5d1fd8a7ff68efb5b351/raw/261f427cb9b9702508670b73b06dd5350d30f373/graphhopper_directions_api.postman_environment.json). 2. Specify [your API key](https://graphhopper.com/dashboard/#/register) in your environment: `\"api_key\": your API key` 3. Start exploring  ![Postman](./img/postman.png)  ## API Client Libraries  To speed up development and make coding easier, we offer the following client libraries:   * [JavaScript client](https://github.com/graphhopper/directions-api-js-client) - try the [live examples](https://graphhopper.com/api/1/examples/)  * [Others](https://github.com/graphhopper/directions-api-clients) like C#, Ruby, PHP, Python, ... automatically created for the Route Optimization API  ### Bandwidth reduction  If you create your own client, make sure it supports http/2 and gzipped responses for best speed.  If you use the Matrix, the Route Optimization API or the Cluster API and want to solve large problems, we recommend you to reduce bandwidth by [compressing your POST request](https://gist.github.com/karussell/82851e303ea7b3459b2dea01f18949f4) and specifying the header as follows: `Content-Encoding: gzip`. This will also avoid the HTTP 413 error \"Request Entity Too Large\".  ## Contact Us  If you have problems or questions, please read the following information:  - [FAQ](https://graphhopper.com/api/1/docs/FAQ/) - [Public forum](https://discuss.graphhopper.com/c/directions-api) - [Contact us](https://www.graphhopper.com/contact-form/) - [GraphHopper Status Page](https://status.graphhopper.com/)  To stay informed about the latest developments, you can  - follow us on [twitter](https://twitter.com/graphhopper/), - read [our blog](https://graphhopper.com/blog/), - sign up for our newsletter or - [our forum](https://discuss.graphhopper.com/c/directions-api).  Select the channel you like the most.   # Map Data and Routing Profiles  Currently, our main data source is [OpenStreetMap](https://www.openstreetmap.org). We also integrated other network data providers. This chapter gives an overview about the options you have.  ## OpenStreetMap  #### Geographical Coverage  [OpenStreetMap](https://www.openstreetmap.org) covers the whole world. If you want to see for yourself if we can provide data suitable for your region, please visit [GraphHopper Maps](https://graphhopper.com/maps/). You can edit and modify OpenStreetMap data if you find that important information is missing, e.g. a weight limit for a bridge. [Here](https://wiki.openstreetmap.org/wiki/Beginners%27_guide) is a beginner's guide that shows how to add data. If you have edited data, we usually consider your data after 1 week at the latest.  #### Supported Routing Profiles  The Routing, Matrix and Route Optimization APIs support the following profiles:  Name             | Description           | Restrictions                        | Icon -----------------|:----------------------|:------------------------------------|:--------------------------------------------------------- car              | Car mode              | car access, weight=2500kg, width=2m, height=2m           | ![car image](https://graphhopper.com/maps/img/car.png) car_delivery     | Car mode              | car access including delivery and private roads | ![car image](https://graphhopper.com/maps/img/car.png) car_avoid_ferry      | Car mode          | car that heavily penalizes ferries          | ![car image](https://graphhopper.com/maps/img/car.png) car_avoid_motorway   | Car mode          | car that heavily penalizes motorways        | ![car image](https://graphhopper.com/maps/img/car.png) car_avoid_toll       | Car mode          | car that heavily penalizes tolls            | ![car image](https://graphhopper.com/maps/img/car.png) small_truck          | Small truck like a Mercedes Sprinter, Ford Transit or Iveco Daily | height=2.7m, width=2+0.34m, length=5.5m, weight=2080+1400 kg | ![small truck image](https://graphhopper.com/maps/img/small_truck.png) small_truck_delivery | Small truck                                             | like small_truck but including delivery and private roads             | ![small truck image](https://graphhopper.com/maps/img/small_truck.png) truck                  | Truck like a MAN or Mercedes-Benz Actros              | height=3.7m, width=2.6+0.34m, length=12m, weight=13000+13000 kg, hgv=yes, 3 Axes | ![truck image](https://graphhopper.com/maps/img/truck.png) scooter                | Moped mode | Fast inner city, often used for food delivery, is able to ignore certain bollards, maximum speed of roughly 50km/h. weight=300kg, width=1m, height=2m | ![scooter image](https://graphhopper.com/maps/img/scooter.png) scooter_delivery       | Moped mode | Like scooter but including delivery and private roads | ![scooter image](https://graphhopper.com/maps/img/scooter.png)     foot       | Pedestrian or walking without dangerous [SAC-scales](https://wiki.openstreetmap.org/wiki/Key:sac_scale) | foot access         | ![foot image](https://graphhopper.com/maps/img/foot.png) hike       | Pedestrian or walking with priority for more beautiful hiking tours and potentially a bit longer than `foot`. Walking duration is influenced by elevation differences.  | foot access         | ![hike image](https://graphhopper.com/maps/img/hike.png) bike       | Trekking bike avoiding hills | bike access         | ![Bike image](https://graphhopper.com/maps/img/bike.png) mtb        | Mountainbike                 | bike access         | ![Mountainbike image](https://graphhopper.com/maps/img/mtb.png) racingbike | Bike preferring roads        | bike access         | ![Racingbike image](https://graphhopper.com/maps/img/racingbike.png)  Please note:   * the free package supports only the routing profiles `car`, `bike` or `foot`  * up to 2 different routing profiles can be used in a single request towards the Route Optimization API. The number of vehicles is unaffected and depends on your subscription.  * we offer custom routing profiles with different properties, different speed profiles or different access options. To find out more about custom profiles, please [contact us](https://www.graphhopper.com/contact-form/).  * a sophisticated `motorcycle` profile is available up on request. It is powered by the [Kurviger](https://kurviger.de/en) Routing API and favors curves and slopes while avoiding cities and highways.   ## TomTom  If you want to include traffic, you can purchase the TomTom Add-on. This Add-on only uses TomTom's road network and historical traffic information. Live traffic is not yet considered. If you are interested to learn how we consider traffic information, we recommend that you read [this article](https://www.graphhopper.com/blog/2017/11/06/time-dependent-optimization/).  Please note the following:   * Currently we only offer this for our [Route Optimization API](#tag/Route-Optimization-API). [Contact us](https://www.graphhopper.com/contact-form/) if you would like to use it for the Matrix or Routing API.  * In addition to our terms, you need to accept TomTom's [End User License Aggreement](https://www.graphhopper.com/tomtom-end-user-license-agreement/).  * We do *not* use TomTom's web services. We only use their data with our software.   [Contact us](https://www.graphhopper.com/contact-form/) if you want to buy this TomTom add-on.  #### Geographical Coverage  We offer  - Europe including Russia - North, Central and South America - Saudi Arabia and United Arab Emirates - South Africa - Southeast Asia - Australia  #### Supported Vehicle Profiles  Name       | Description           | Restrictions              | Icon -----------|:----------------------|:--------------------------|:--------------------------------------------------------- car        | Car mode              | car access                | ![car image](https://graphhopper.com/maps/img/car.png) small_truck| Small truck like a Mercedes Sprinter, Ford Transit or Iveco Daily | height=2.7m, width=2+0.4m, length=5.5m, weight=2080+1400 kg | ![small truck image](https://graphhopper.com/maps/img/small_truck.png)    # Custom Model  A custom model allows you to modify the default routing behavior of a vehicle profile by specifying a set of rules in JSON language. There are three JSON properties to change a profile: `priority`, `speed` and `distance_influence` that are described in great detail in the next sections.  But first we will give an introductory example for each of these JSON properties. Let's start with `speed`:  ```json {   \"speed\": [{     \"if\": \"road_class == MOTORWAY\",     \"limit_to\": 90   }] } ```  As you might have already guessed this limits the speed on motorways to 90km/h. Changing the speed will of course change the travel time, but at the same time this makes other road classes more likely as well, so you can use this model to avoid motorways.  You can immediately try this out in the Browser [on GraphHopper Maps](https://graphhopper.com/maps/?point=50.856527%2C12.876127&point=51.02952%2C13.295603&profile=car&custom_model=%7B%22speed%22%3A%5B%7B%22if%22%3A%22road_class+=%3D+MOTORWAY%22%2C%22limit_to%22%3A90%7D%5D%7D). GraphHopper Maps offers an interactive text editor to comfortably enter custom models. You can open it by pressing the \"custom\" button. It will check the syntax of your custom model and mark errors in red. You can press Ctrl+Space or Alt+Enter to retrieve auto-complete suggestions. Pressing Ctrl+Enter will send a routing request for the custom model you entered. To disable the custom model you click the \"custom\" button again.   In the second example we show how to avoid certain road classes without changing the travel time:  ```json {   \"priority\": [{     \"if\": \"road_class == LIVING_STREET || road_class == RESIDENTIAL || road_class == UNCLASSIFIED\",     \"multiply_by\": 0.1   }] } ```  This example avoids certain smaller streets. [View it in GraphHopper Maps](https://graphhopper.com/maps/?point=51.125708%2C13.067915&point=51.125964%2C13.082271&profile=car&custom_model=%7B%22priority%22%3A%5B%7B%22if%22%3A%22road_class+=%3D+LIVING_STREET+%7C%7C+road_class+%3D%3D+RESIDENTIAL+%7C%7C+road_class+%3D%3D+UNCLASSIFIED%22%2C%22multiply_by%22%3A0.1%7D%5D%7D).  The third example shows how to prefer shortest paths:  ```json {   \"distance_influence\": 200 } ```  [View this example in GraphHopper Maps](https://graphhopper.com/maps/?point=51.04188%2C13.057766&point=51.057527%2C13.068237&profile=car&custom_model=%7B%22distance_influence%22%3A200%7D).  There is a fourth JSON property `areas` that allows you to define areas that can then be used in the `if` or `else_if` conditions for `speed` and `priority`. Please read more about this and the other properties below and try some examples in [GraphHopper Maps](https://graphhopper.com/maps/) with the help of [this blog post](https://www.graphhopper.com/blog/2020/05/31/examples-for-customizable-routing/).   ## Customizing speed  When using custom models you do not need to define rules that specify a speed for every road segment, but rather GraphHopper assumes a default speed. All you need to do is adjust this default speed to your use-case as you will always use the custom  model in conjunction with a routing profile which is used to determine the default speed.  The custom model is a JSON object and the first property we will learn about here is the `speed` property. The `speed` property's value is a list of conditional statements that modify the default speed. Every such statement consists of a condition and an operation. The different statements are applied to the default speed from top to bottom, i.e. statements that come later in the list are applied to the resulting value of previous operations. Each statement is only executed if the corresponding condition applies for the current road segment. This will become more clear in the following examples.  Currently the custom model language supports two operators:  - `multiply_by` multiplies the speed value with a given number - `limit_to` limits the speed value to a given number  #### `if` statements and the `multiply_by` operation  Let's start with a simple example using `multiply_by`:  ```json {   \"speed\": [     {       \"if\": \"road_class == MOTORWAY\",       \"multiply_by\": 0.5     }   ] } ```  This custom model reduces the speed of every road segment for which the `road_class` attribute is `MOTORWAY` to fifty percent of the default speed (the default speed is multiplied by `0.5`). Again, the default speed is the speed that GraphHopper would normally use for the profile's vehicle. Note the `if` clause which means that the operation (`multiply_by`) is only applied *if* the condition `road_class == MOTORWAY` is fulfilled for the road segment under consideration. The `==` indicates equality, i.e. the condition reads \"the road_class equals MOTORWAY\". If you're a bit familiar with programming note that the condition (the value of the `if` key) is just a boolean condition in Java language (other programming languages like C or JavaScript are very similar in this regard). A more complex condition could look like this: `road_class == PRIMARY || road_class == TERTIARY` which uses the **or** (`||`) operator and literally means \"road_class equals PRIMARY or road_class equals TERTIARY\".  There can be multiple such 'if statements' in the speed section, and they are evaluated from top to bottom:  ```json {   \"speed\": [     {       \"if\": \"road_class == MOTORWAY\",       \"multiply_by\": 0.5     },     {       \"if\": \"road_class == PRIMARY || road_environment == TUNNEL\",       \"multiply_by\": 0.7     }   ] } ```  In this example the default speed of road segments with `road_class == MOTORWAY` will be multiplied by `0.5`, the default speed of road segments with `road_class == PRIMARY` will be multiplied by `0.7` and for road segments with both `road_class == MOTORWAY` and `road_environment == TUNNEL` the default speed will be multiplied first by `0.5` and then by `0.7`. So overall the default speed will be multiplied by `0.35`. For road segments with `road_class == PRIMARY` and `road_environment == TUNNEL` we only multiply by `0.7`, even though both parts of the second condition apply. It only matters whether the road segment matches the condition or not.  `road_class` and `road_environment` are road attributes of 'enum' type, i.e. their value can only be one of a fixed set of values, like `MOTORWAY` for `road_class`.  Other road attributes like `get_off_bike` are of `boolean` type. They can be used as conditions directly, for example:  ```json {   \"speed\": [     {       \"if\": \"get_off_bike\",       \"multiply_by\": 0.6     }   ] } ```  which means that for road segments with `get_off_bike==true` the speed factor will be `0.6`.  For attributes with numeric values, like `max_width` you should not use the `==` (equality) or `!=` ( inequality) operators, but the numerical comparison operators \"bigger\" `>`, \"bigger or equals\" `>=`, \"smaller\" `<`, or \"smaller or equals\" `<=`, e.g.:  ```json {   \"speed\": [     {       \"if\": \"max_width < 2.5\",       \"multiply_by\": 0.8     }   ] } ```   which means that for all road segments with `max_width` smaller than `2.5m` the speed is multiplied by `0.8`.   ### The `limit_to` operation  Besides the `multiply_by` operator there is also the `limit_to` operator. As the name suggests `limit_to` limits the current value to the given value. Take this example:  ```json {   \"speed\": [     {       \"if\": \"road_class == MOTORWAY\",       \"multiply_by\": 0.8     },     {       \"if\": \"surface == GRAVEL\",       \"limit_to\": 60     }   ] } ```  This implies that on all road segments with the `GRAVEL` value for `surface` the speed will be at most `60km/h`, regardless of the default speed and the previous rules. So for a road segment with `road_class == MOTORWAY`, `surface == GRAVEL` and default speed `100` the first statement reduces the speed from `100` to `80` and the second statement further reduces the speed from `80` to `60`. If the `road_class` was `PRIMARY` and the default speed was `50` the first rule would not apply and the second rule would do nothing, because limiting `50` to `60` still yields `50`.  Note that all values used for `limit_to` must be in the range `[0, max_vehicle_speed]` where `max_vehicle_speed` is the maximum speed that is set for the base vehicle and cannot be changed.  A common use-case for the `limit_to` operation is the following pattern:  ```json {   \"speed\": [     {       \"if\": \"true\",       \"limit_to\": 90     }   ] } ```  which means that the speed is limited to `90km/h` for all road segments regardless of its properties. The condition \"`true`\" is always fulfilled.  ### `else` and `else_if` statements  The `else` statement allows you to define that some operations should be applied if an road segment does **not** match a condition. So this example:  ```json {   \"speed\": [     {       \"if\": \"road_class == MOTORWAY\",       \"multiply_by\": 0.5     },     {       \"else\": \"\",       \"limit_to\": 50     }   ] } ```  means that for all road segments with `road_class == MOTORWAY` we multiply the default speed by `0.5` and for all others we limit the default speed to `50` (but never both).  In case you want to distinguish more than two cases (road segments that match or match not a condition) you can use `else_if` statements which are only evaluated in case the previous `if` or `else_if` statement did **not** match:  ```json {   \"speed\": [     {       \"if\": \"road_class == MOTORWAY\",       \"multiply_by\": 0.5     },     {       \"else_if\": \"road_environment == TUNNEL\",       \"limit_to\": 70     },     {       \"else\": \"\",       \"multiply_by\": 0.9     }   ] } ```  So if the first condition matches (`road_class == MOTORWAY`) the default speed is multiplied by `0.5`, but the other two statements are ignored. Only if the first statement does not match (e.g. `road_class == PRIMARY`) the second statement is even considered and only if it matches (`road_environment == TUNNEL`) the default speed is limited to 70. The last operation (`multiply_by: 0.9`) is only applied if both previous conditions did not match.  `else` and `else_if` statements always require a preceding `if` or `else_if` statement. However, there can be multiple 'blocks' of subsequent `if/else_if/else` statements in the list of rules for `speed`.  `else_if` is useful for example in case you have multiple `multiply_by` operations, but you do not want that the speed gets reduced by all of them. For the following model  ```json {   \"speed\": [     {       \"if\": \"road_class == MOTORWAY\",       \"multiply_by\": 0.5     },     {       \"else_if\": \"road_environment == TUNNEL\",       \"multiply_by\": 0.8     }   ] } ```  only the first factor (`0.5`) will be applied even for road segments that fulfill both conditions.  ## Limit rules to certain areas  You can not only modify the speed of road segments based on properties, like we saw in the previous examples, but you can also modify the speed of road segments based on their location. To do this you need to first create and add some areas to the `areas` section of the custom model. You can then use the name of these areas in the conditions of your `if/else/else_if` statements.  In the following example we multiply the speed of all road segments in an area called `custom1` with `0.7` and also limit it to `50km/h`. Note that each area's name needs to be prefixed with `in_`:  ```json {   \"speed\": [     {       \"if\": \"in_custom1\",       \"multiply_by\": 0.7     },     {       \"if\": \"in_custom1\",       \"limit_to\": 50     }   ],   \"areas\": {     \"custom1\": {       \"type\": \"Feature\",       \"id\": \"something\",       \"properties\": {},       \"geometry\": {         \"type\": \"Polygon\",         \"coordinates\": [           [             [               1.525,               42.511             ],             [               1.510,               42.503             ],             [               1.531,               42.495             ],             [               1.542,               42.505             ],             [               1.525,               42.511             ]           ]         ]       }     }   } } ```  Areas are given in GeoJson format, but currently only the exact format in the above example is supported, i.e. one object with type `Feature`, a geometry with type `Polygon` and optional (but ignored) `id` and `properties` fields. Note that the coordinates array of `Polygon` is an array of arrays that each must describe a closed ring, i.e. the first point must be equal to the last. Each point is given as an array [longitude, latitude], so the coordinates array has three dimensions total.  Using the `areas` feature you can also block entire areas i.e. by multiplying the speed with `0`, but for this you should rather use the `priority` section that we will explain next.  ## Customizing priority  Make sure you read the introductory section of this document to learn what the `priority` factor means. In short it allows similar modifications as `speed`, but instead of modifying the road segment weights *and* travel times it will only affect the weights. By default, the priority is `1` for every road segment, so it does not affect the weight. However, changing the priority of a road can yield a relative weight difference in comparison to other roads.  Customizing the `priority` works very much like changing the `speed`, so in case you did not read the section about `speed` you should go back there and read it now. The only real difference is that there is no `limit_to` operator for `priority`. As a quick reminder here is an example for priority:  ```json {   \"priority\": [     {       \"if\": \"road_class == MOTORWAY\",       \"multiply_by\": 0.5     },     {       \"else_if\": \"road_class == SECONDARY\",       \"multiply_by\": 0.9     },     {       \"if\": \"road_environment == TUNNEL\",       \"multiply_by\": 0.1     }   ] } ```  means that road segments with `road_class==MOTORWAY` and `road_environment==TUNNEL` get priority `0.5*0.1=0.05` and those with `road_class==SECONDARY` and no TUNNEL, get priority `0.9` and so on.  Edges with lower priority values will be less likely part of the optimal route calculated by GraphHopper, higher values mean that these road segments shall be preferred. If you do not want to state which road segments shall be avoided, but rather which ones shall be preferred, you need to **decrease** the priority of others:  ```json {   \"priority\": [     {       \"if\": \"road_class != CYCLEWAY\",       \"multiply_by\": 0.8     }   ] } ```  means decreasing the priority for all road_classes *except* cycleways.  Just like we saw for `speed` you can also adjust the priority for road segments in a certain area. It works exactly the same way:  ```json {   \"priority\": [     {       \"if\": \"in_custom1\",       \"multiply_by\": 0.7     }   ] } ```  To block an entire area set the priority value to `0`. You can even set the priority only for certain roads in an area like this:  ```json {   \"priority\": [     {       \"if\": \"road_class == MOTORWAY && in_custom1\",       \"multiply_by\": 0.1     }   ] } ```  Some other useful attributes to restrict access to certain roads depending on your vehicle dimensions are the following:  ```json {   \"priority\": [     {       \"if\": \"max_width < 2.5\",       \"multiply_by\": 0     },     {       \"if\": \"max_length < 10\",       \"multiply_by\": 0     },     {       \"if\": \"max_weight < 3.5\",       \"multiply_by\": 0     }   ] } ```  which means that the priority for all road segments that allow a maximum vehicle width of `2.5m`, a maximum vehicle length of `10m` or a maximum vehicle weight of `3.5tons`, or less, is zero, i.e. these \"narrow\" road segments are blocked.  ## Customizing distance_influence  The `distance_influence` property allows you to control the trade-off between a fast route (minimum time) and a short route (minimum distance). The larger `distance_influence` is the more GraphHopper will prioritize routes with a small total distance. More precisely, the `distance_influence` is the time you need to save on a detour (a longer distance route option) such that you prefer taking the detour compared to a shorter route.   A value of `100` means that one extra kilometer of detour must save you `100s` of travelling time or else you are not  willing to take the detour. Or to put it another way, if a reference route takes `600s` and is `10km` long,  `distance_influence=100` means that you are willing to take an alternative route that is `11km` long only if  it takes no longer than `500s` (saves `100s`). Things get a bit more complicated when `priority` is not `1`, but the  effect stays the same: The larger `distance_influence` is, the more GraphHopper will focus on finding short routes.   ## Road attributes  GraphHopper stores different attributes for every road segment. Some frequently used are the following (some of their possible values are given in brackets):  - road_class: (OTHER, MOTORWAY, TRUNK, PRIMARY, SECONDARY, TRACK, STEPS, CYCLEWAY, FOOTWAY, ...) - road_environment: (ROAD, FERRY, BRIDGE, TUNNEL, ...) - road_access: (DESTINATION, DELIVERY, PRIVATE, NO, ...) - surface: (PAVED, DIRT, SAND, GRAVEL, ...) - smoothness: (EXCELLENT, GOOD, INTERMEDIATE, ...) - toll: (NO, ALL, HGV)  To learn about all available attributes you can query the `/info` endpoint or use auto complete in GraphHopper Maps.  Besides these road attributes, which can take distinct string values, there are also some that represent a boolean value (they are either true or false for a given road segment), like:  - get_off_bike - road_class_link  There are also some that take on a numeric value, like:  - max_weight - max_height - max_width  ## Limitations  Custom models are currently:  1. only available for the [POST Route Endpoint](#operation/postRoute). If you are interested in using this for the Matrix or Route Optimization API please [contact us](https://www.graphhopper.com/contact-form/) to get access to an early alpha version. For the Isochrone API it is also planned. 2. only available for the following parent profiles: `foot`, `bike`, `scooter`, `car` and `small_truck`. 3. only available for OpenStreetMap.  This feature will strongly benefit from feedback, so do not hesitate to share your experience, your favorite custom model or some of the problems you ran into when you tried building your own with custom model.  ## Troubleshooting  ### Recommendations  For debugging you can use the custom model editor in [GraphHopper Maps](https://graphhopper.com/maps/) (click the 'custom' button).  When debugging problems with custom models you should first try if your request goes through without an error using an empty custom model.  For production you should avoid to include road_access and toll in the profile as we will change their values in the next weeks which could cause unexpected problems.  ### All routes for my custom model fail  This could mean that either your custom model made some of the roads near the start and destination inaccessible,  then usually we return a PointNotFoundException with the point_index with the \"location snap\" problem.  Or, the custom model made all roads between your start and destination inaccessible, then we return a ConnectionNotFoundException. This happens e.g. when you exclude tunnels,  ferries or motorways but all routes between start and destination have these road attributes satisfied, i.e. we cannot find a route.  **Solution**: relax your custom model and e.g. instead of excluding certain road attributes via `\"multiply_by\": 0` you should try to use `0.01`.   # noqa: E501

    The version of the OpenAPI document: 1.0.0
    Contact: support@graphhopper.com
    Generated by: https://openapi-generator.tech
"""


import json
import atexit
import mimetypes
from multiprocessing.pool import ThreadPool
import io
import os
import re
import typing
from urllib.parse import quote
from urllib3.fields import RequestField


from openapi_client import rest
from openapi_client.configuration import Configuration
from openapi_client.exceptions import ApiTypeError, ApiValueError, ApiException
from openapi_client.model_utils import (
    ModelNormal,
    ModelSimple,
    ModelComposed,
    check_allowed_values,
    check_validations,
    date,
    datetime,
    deserialize_file,
    file_type,
    model_to_dict,
    none_type,
    validate_and_convert_types
)


class ApiClient(object):
    """Generic API client for OpenAPI client library builds.

    OpenAPI generic API client. This client handles the client-
    server communication, and is invariant across implementations. Specifics of
    the methods and models for each application are generated from the OpenAPI
    templates.

    NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech
    Do not edit the class manually.

    :param configuration: .Configuration object for this client
    :param header_name: a header to pass when making calls to the API.
    :param header_value: a header value to pass when making calls to
        the API.
    :param cookie: a cookie to include in the header when making calls
        to the API
    :param pool_threads: The number of threads to use for async requests
        to the API. More threads means more concurrent API requests.
    """

    _pool = None

    def __init__(self, configuration=None, header_name=None, header_value=None,
                 cookie=None, pool_threads=1):
        if configuration is None:
            configuration = Configuration.get_default_copy()
        self.configuration = configuration
        self.pool_threads = pool_threads

        self.rest_client = rest.RESTClientObject(configuration)
        self.default_headers = {}
        if header_name is not None:
            self.default_headers[header_name] = header_value
        self.cookie = cookie
        # Set default User-Agent.
        self.user_agent = 'OpenAPI-Generator/1.0.0/python'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        if self._pool:
            self._pool.close()
            self._pool.join()
            self._pool = None
            if hasattr(atexit, 'unregister'):
                atexit.unregister(self.close)

    @property
    def pool(self):
        """Create thread pool on first request
         avoids instantiating unused threadpool for blocking clients.
        """
        if self._pool is None:
            atexit.register(self.close)
            self._pool = ThreadPool(self.pool_threads)
        return self._pool

    @property
    def user_agent(self):
        """User agent for this API client"""
        return self.default_headers['User-Agent']

    @user_agent.setter
    def user_agent(self, value):
        self.default_headers['User-Agent'] = value

    def set_default_header(self, header_name, header_value):
        self.default_headers[header_name] = header_value

    def __call_api(
        self,
        resource_path: str,
        method: str,
        path_params: typing.Optional[typing.Dict[str, typing.Any]] = None,
        query_params: typing.Optional[typing.List[typing.Tuple[str, typing.Any]]] = None,
        header_params: typing.Optional[typing.Dict[str, typing.Any]] = None,
        body: typing.Optional[typing.Any] = None,
        post_params: typing.Optional[typing.List[typing.Tuple[str, typing.Any]]] = None,
        files: typing.Optional[typing.Dict[str, typing.List[io.IOBase]]] = None,
        response_type: typing.Optional[typing.Tuple[typing.Any]] = None,
        auth_settings: typing.Optional[typing.List[str]] = None,
        _return_http_data_only: typing.Optional[bool] = None,
        collection_formats: typing.Optional[typing.Dict[str, str]] = None,
        _preload_content: bool = True,
        _request_timeout: typing.Optional[typing.Union[int, float, typing.Tuple]] = None,
        _host: typing.Optional[str] = None,
        _check_type: typing.Optional[bool] = None,
        _content_type: typing.Optional[str] = None,
        _request_auths: typing.Optional[typing.List[typing.Dict[str, typing.Any]]] = None
    ):

        config = self.configuration

        # header parameters
        header_params = header_params or {}
        header_params.update(self.default_headers)
        if self.cookie:
            header_params['Cookie'] = self.cookie
        if header_params:
            header_params = self.sanitize_for_serialization(header_params)
            header_params = dict(self.parameters_to_tuples(header_params,
                                                           collection_formats))

        # path parameters
        if path_params:
            path_params = self.sanitize_for_serialization(path_params)
            path_params = self.parameters_to_tuples(path_params,
                                                    collection_formats)
            for k, v in path_params:
                # specified safe chars, encode everything
                resource_path = resource_path.replace(
                    '{%s}' % k,
                    quote(str(v), safe=config.safe_chars_for_path_param)
                )

        # query parameters
        if query_params:
            query_params = self.sanitize_for_serialization(query_params)
            query_params = self.parameters_to_tuples(query_params,
                                                     collection_formats)

        # post parameters
        if post_params or files:
            post_params = post_params if post_params else []
            post_params = self.sanitize_for_serialization(post_params)
            post_params = self.parameters_to_tuples(post_params,
                                                    collection_formats)
            post_params.extend(self.files_parameters(files))
            if header_params['Content-Type'].startswith("multipart"):
                post_params = self.parameters_to_multipart(post_params,
                                                           (dict))

        # body
        if body:
            body = self.sanitize_for_serialization(body)

        # auth setting
        self.update_params_for_auth(header_params, query_params,
                                    auth_settings, resource_path, method, body,
                                    request_auths=_request_auths)

        # request url
        if _host is None:
            url = self.configuration.host + resource_path
        else:
            # use server/host defined in path or operation instead
            url = _host + resource_path

        try:
            # perform request and return response
            response_data = self.request(
                method, url, query_params=query_params, headers=header_params,
                post_params=post_params, body=body,
                _preload_content=_preload_content,
                _request_timeout=_request_timeout)
        except ApiException as e:
            e.body = e.body.decode('utf-8')
            raise e

        self.last_response = response_data

        return_data = response_data

        if not _preload_content:
            return (return_data)
            return return_data

        # deserialize response data
        if response_type:
            if response_type != (file_type,):
                encoding = "utf-8"
                content_type = response_data.getheader('content-type')
                if content_type is not None:
                    match = re.search(r"charset=([a-zA-Z\-\d]+)[\s\;]?", content_type)
                    if match:
                        encoding = match.group(1)
                response_data.data = response_data.data.decode(encoding)

            return_data = self.deserialize(
                response_data,
                response_type,
                _check_type
            )
        else:
            return_data = None

        if _return_http_data_only:
            return (return_data)
        else:
            return (return_data, response_data.status,
                    response_data.getheaders())

    def parameters_to_multipart(self, params, collection_types):
        """Get parameters as list of tuples, formatting as json if value is collection_types

        :param params: Parameters as list of two-tuples
        :param dict collection_types: Parameter collection types
        :return: Parameters as list of tuple or urllib3.fields.RequestField
        """
        new_params = []
        if collection_types is None:
            collection_types = (dict)
        for k, v in params.items() if isinstance(params, dict) else params:  # noqa: E501
            if isinstance(
                     v, collection_types): # v is instance of collection_type, formatting as application/json
                v = json.dumps(v, ensure_ascii=False).encode("utf-8")
                field = RequestField(k, v)
                field.make_multipart(content_type="application/json; charset=utf-8")
                new_params.append(field)
            else:
                new_params.append((k, v))
        return new_params

    @classmethod
    def sanitize_for_serialization(cls, obj):
        """Prepares data for transmission before it is sent with the rest client
        If obj is None, return None.
        If obj is str, int, long, float, bool, return directly.
        If obj is datetime.datetime, datetime.date
            convert to string in iso8601 format.
        If obj is list, sanitize each element in the list.
        If obj is dict, return the dict.
        If obj is OpenAPI model, return the properties dict.
        If obj is io.IOBase, return the bytes
        :param obj: The data to serialize.
        :return: The serialized form of data.
        """
        if isinstance(obj, (ModelNormal, ModelComposed)):
            return {
                key: cls.sanitize_for_serialization(val) for key,
                val in model_to_dict(
                    obj,
                    serialize=True).items()}
        elif isinstance(obj, io.IOBase):
            return cls.get_file_data_and_close_file(obj)
        elif isinstance(obj, (str, int, float, none_type, bool)):
            return obj
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, ModelSimple):
            return cls.sanitize_for_serialization(obj.value)
        elif isinstance(obj, (list, tuple)):
            return [cls.sanitize_for_serialization(item) for item in obj]
        if isinstance(obj, dict):
            return {key: cls.sanitize_for_serialization(val) for key, val in obj.items()}
        raise ApiValueError(
            'Unable to prepare type {} for serialization'.format(
                obj.__class__.__name__))

    def deserialize(self, response, response_type, _check_type):
        """Deserializes response into an object.

        :param response: RESTResponse object to be deserialized.
        :param response_type: For the response, a tuple containing:
            valid classes
            a list containing valid classes (for list schemas)
            a dict containing a tuple of valid classes as the value
            Example values:
            (str,)
            (Pet,)
            (float, none_type)
            ([int, none_type],)
            ({str: (bool, str, int, float, date, datetime, str, none_type)},)
        :param _check_type: boolean, whether to check the types of the data
            received from the server
        :type _check_type: bool

        :return: deserialized object.
        """
        # handle file downloading
        # save response body into a tmp file and return the instance
        if response_type == (file_type,):
            content_disposition = response.getheader("Content-Disposition")
            return deserialize_file(response.data, self.configuration,
                                    content_disposition=content_disposition)

        # fetch data from response object
        try:
            received_data = json.loads(response.data)
        except ValueError:
            received_data = response.data

        # store our data under the key of 'received_data' so users have some
        # context if they are deserializing a string and the data type is wrong
        deserialized_data = validate_and_convert_types(
            received_data,
            response_type,
            ['received_data'],
            True,
            _check_type,
            configuration=self.configuration
        )
        return deserialized_data

    def call_api(
        self,
        resource_path: str,
        method: str,
        path_params: typing.Optional[typing.Dict[str, typing.Any]] = None,
        query_params: typing.Optional[typing.List[typing.Tuple[str, typing.Any]]] = None,
        header_params: typing.Optional[typing.Dict[str, typing.Any]] = None,
        body: typing.Optional[typing.Any] = None,
        post_params: typing.Optional[typing.List[typing.Tuple[str, typing.Any]]] = None,
        files: typing.Optional[typing.Dict[str, typing.List[io.IOBase]]] = None,
        response_type: typing.Optional[typing.Tuple[typing.Any]] = None,
        auth_settings: typing.Optional[typing.List[str]] = None,
        async_req: typing.Optional[bool] = None,
        _return_http_data_only: typing.Optional[bool] = None,
        collection_formats: typing.Optional[typing.Dict[str, str]] = None,
        _preload_content: bool = True,
        _request_timeout: typing.Optional[typing.Union[int, float, typing.Tuple]] = None,
        _host: typing.Optional[str] = None,
        _check_type: typing.Optional[bool] = None,
        _request_auths: typing.Optional[typing.List[typing.Dict[str, typing.Any]]] = None
    ):
        """Makes the HTTP request (synchronous) and returns deserialized data.

        To make an async_req request, set the async_req parameter.

        :param resource_path: Path to method endpoint.
        :param method: Method to call.
        :param path_params: Path parameters in the url.
        :param query_params: Query parameters in the url.
        :param header_params: Header parameters to be
            placed in the request header.
        :param body: Request body.
        :param post_params dict: Request post form parameters,
            for `application/x-www-form-urlencoded`, `multipart/form-data`.
        :param auth_settings list: Auth Settings names for the request.
        :param response_type: For the response, a tuple containing:
            valid classes
            a list containing valid classes (for list schemas)
            a dict containing a tuple of valid classes as the value
            Example values:
            (str,)
            (Pet,)
            (float, none_type)
            ([int, none_type],)
            ({str: (bool, str, int, float, date, datetime, str, none_type)},)
        :param files: key -> field name, value -> a list of open file
            objects for `multipart/form-data`.
        :type files: dict
        :param async_req bool: execute request asynchronously
        :type async_req: bool, optional
        :param _return_http_data_only: response data without head status code
                                       and headers
        :type _return_http_data_only: bool, optional
        :param collection_formats: dict of collection formats for path, query,
            header, and post parameters.
        :type collection_formats: dict, optional
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :type _preload_content: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :param _check_type: boolean describing if the data back from the server
            should have its type checked.
        :type _check_type: bool, optional
        :param _request_auths: set to override the auth_settings for an a single
                              request; this effectively ignores the authentication
                              in the spec for a single request.
        :type _request_auths: list, optional
        :return:
            If async_req parameter is True,
            the request will be called asynchronously.
            The method will return the request thread.
            If parameter async_req is False or missing,
            then the method will return the response directly.
        """
        if not async_req:
            return self.__call_api(resource_path, method,
                                   path_params, query_params, header_params,
                                   body, post_params, files,
                                   response_type, auth_settings,
                                   _return_http_data_only, collection_formats,
                                   _preload_content, _request_timeout, _host,
                                   _check_type, _request_auths=_request_auths)

        return self.pool.apply_async(self.__call_api, (resource_path,
                                                       method, path_params,
                                                       query_params,
                                                       header_params, body,
                                                       post_params, files,
                                                       response_type,
                                                       auth_settings,
                                                       _return_http_data_only,
                                                       collection_formats,
                                                       _preload_content,
                                                       _request_timeout,
                                                       _host, _check_type, None, _request_auths))

    def request(self, method, url, query_params=None, headers=None,
                post_params=None, body=None, _preload_content=True,
                _request_timeout=None):
        """Makes the HTTP request using RESTClient."""
        if method == "GET":
            return self.rest_client.GET(url,
                                        query_params=query_params,
                                        _preload_content=_preload_content,
                                        _request_timeout=_request_timeout,
                                        headers=headers)
        elif method == "HEAD":
            return self.rest_client.HEAD(url,
                                         query_params=query_params,
                                         _preload_content=_preload_content,
                                         _request_timeout=_request_timeout,
                                         headers=headers)
        elif method == "OPTIONS":
            return self.rest_client.OPTIONS(url,
                                            query_params=query_params,
                                            headers=headers,
                                            post_params=post_params,
                                            _preload_content=_preload_content,
                                            _request_timeout=_request_timeout,
                                            body=body)
        elif method == "POST":
            return self.rest_client.POST(url,
                                         query_params=query_params,
                                         headers=headers,
                                         post_params=post_params,
                                         _preload_content=_preload_content,
                                         _request_timeout=_request_timeout,
                                         body=body)
        elif method == "PUT":
            return self.rest_client.PUT(url,
                                        query_params=query_params,
                                        headers=headers,
                                        post_params=post_params,
                                        _preload_content=_preload_content,
                                        _request_timeout=_request_timeout,
                                        body=body)
        elif method == "PATCH":
            return self.rest_client.PATCH(url,
                                          query_params=query_params,
                                          headers=headers,
                                          post_params=post_params,
                                          _preload_content=_preload_content,
                                          _request_timeout=_request_timeout,
                                          body=body)
        elif method == "DELETE":
            return self.rest_client.DELETE(url,
                                           query_params=query_params,
                                           headers=headers,
                                           _preload_content=_preload_content,
                                           _request_timeout=_request_timeout,
                                           body=body)
        else:
            raise ApiValueError(
                "http method must be `GET`, `HEAD`, `OPTIONS`,"
                " `POST`, `PATCH`, `PUT` or `DELETE`."
            )

    def parameters_to_tuples(self, params, collection_formats):
        """Get parameters as list of tuples, formatting collections.

        :param params: Parameters as dict or list of two-tuples
        :param dict collection_formats: Parameter collection formats
        :return: Parameters as list of tuples, collections formatted
        """
        new_params = []
        if collection_formats is None:
            collection_formats = {}
        for k, v in params.items() if isinstance(params, dict) else params:  # noqa: E501
            if k in collection_formats:
                collection_format = collection_formats[k]
                if collection_format == 'multi':
                    new_params.extend((k, value) for value in v)
                else:
                    if collection_format == 'ssv':
                        delimiter = ' '
                    elif collection_format == 'tsv':
                        delimiter = '\t'
                    elif collection_format == 'pipes':
                        delimiter = '|'
                    else:  # csv is the default
                        delimiter = ','
                    new_params.append(
                        (k, delimiter.join(str(value) for value in v)))
            else:
                new_params.append((k, v))
        return new_params

    @staticmethod
    def get_file_data_and_close_file(file_instance: io.IOBase) -> bytes:
        file_data = file_instance.read()
        file_instance.close()
        return file_data

    def files_parameters(self,
                         files: typing.Optional[typing.Dict[str,
                                                            typing.List[io.IOBase]]] = None):
        """Builds form parameters.

        :param files: None or a dict with key=param_name and
            value is a list of open file objects
        :return: List of tuples of form parameters with file data
        """
        if files is None:
            return []

        params = []
        for param_name, file_instances in files.items():
            if file_instances is None:
                # if the file field is nullable, skip None values
                continue
            for file_instance in file_instances:
                if file_instance is None:
                    # if the file field is nullable, skip None values
                    continue
                if file_instance.closed is True:
                    raise ApiValueError(
                        "Cannot read a closed file. The passed in file_type "
                        "for %s must be open." % param_name
                    )
                filename = os.path.basename(file_instance.name)
                filedata = self.get_file_data_and_close_file(file_instance)
                mimetype = (mimetypes.guess_type(filename)[0] or
                            'application/octet-stream')
                params.append(
                    tuple([param_name, tuple([filename, filedata, mimetype])]))

        return params

    def select_header_accept(self, accepts):
        """Returns `Accept` based on an array of accepts provided.

        :param accepts: List of headers.
        :return: Accept (e.g. application/json).
        """
        if not accepts:
            return

        accepts = [x.lower() for x in accepts]

        if 'application/json' in accepts:
            return 'application/json'
        else:
            return ', '.join(accepts)

    def select_header_content_type(self, content_types, method=None, body=None):
        """Returns `Content-Type` based on an array of content_types provided.

        :param content_types: List of content-types.
        :param method: http method (e.g. POST, PATCH).
        :param body: http body to send.
        :return: Content-Type (e.g. application/json).
        """
        if not content_types:
            return None

        content_types = [x.lower() for x in content_types]

        if (method == 'PATCH' and
                'application/json-patch+json' in content_types and
                isinstance(body, list)):
            return 'application/json-patch+json'

        if 'application/json' in content_types or '*/*' in content_types:
            return 'application/json'
        else:
            return content_types[0]

    def update_params_for_auth(self, headers, queries, auth_settings,
                               resource_path, method, body, request_auths=None):
        """Updates header and query params based on authentication setting.

        :param headers: Header parameters dict to be updated.
        :param queries: Query parameters tuple list to be updated.
        :param auth_settings: Authentication setting identifiers list.
        :param resource_path: A string representation of the HTTP request resource path.
        :param method: A string representation of the HTTP request method.
        :param body: A object representing the body of the HTTP request.
            The object type is the return value of _encoder.default().
        :param request_auths: if set, the provided settings will
            override the token in the configuration.
        """
        if not auth_settings:
            return

        if request_auths:
            for auth_setting in request_auths:
                self._apply_auth_params(
                    headers, queries, resource_path, method, body, auth_setting)
            return

        for auth in auth_settings:
            auth_setting = self.configuration.auth_settings().get(auth)
            if auth_setting:
                self._apply_auth_params(
                    headers, queries, resource_path, method, body, auth_setting)

    def _apply_auth_params(self, headers, queries, resource_path, method, body, auth_setting):
        if auth_setting['in'] == 'cookie':
            headers['Cookie'] = auth_setting['key'] + "=" + auth_setting['value']
        elif auth_setting['in'] == 'header':
            if auth_setting['type'] != 'http-signature':
                headers[auth_setting['key']] = auth_setting['value']
        elif auth_setting['in'] == 'query':
            queries.append((auth_setting['key'], auth_setting['value']))
        else:
            raise ApiValueError(
                'Authentication token must be in `query` or `header`'
            )


class Endpoint(object):
    def __init__(self, settings=None, params_map=None, root_map=None,
                 headers_map=None, api_client=None, callable=None):
        """Creates an endpoint

        Args:
            settings (dict): see below key value pairs
                'response_type' (tuple/None): response type
                'auth' (list): a list of auth type keys
                'endpoint_path' (str): the endpoint path
                'operation_id' (str): endpoint string identifier
                'http_method' (str): POST/PUT/PATCH/GET etc
                'servers' (list): list of str servers that this endpoint is at
            params_map (dict): see below key value pairs
                'all' (list): list of str endpoint parameter names
                'required' (list): list of required parameter names
                'nullable' (list): list of nullable parameter names
                'enum' (list): list of parameters with enum values
                'validation' (list): list of parameters with validations
            root_map
                'validations' (dict): the dict mapping endpoint parameter tuple
                    paths to their validation dictionaries
                'allowed_values' (dict): the dict mapping endpoint parameter
                    tuple paths to their allowed_values (enum) dictionaries
                'openapi_types' (dict): param_name to openapi type
                'attribute_map' (dict): param_name to camelCase name
                'location_map' (dict): param_name to  'body', 'file', 'form',
                    'header', 'path', 'query'
                collection_format_map (dict): param_name to `csv` etc.
            headers_map (dict): see below key value pairs
                'accept' (list): list of Accept header strings
                'content_type' (list): list of Content-Type header strings
            api_client (ApiClient) api client instance
            callable (function): the function which is invoked when the
                Endpoint is called
        """
        self.settings = settings
        self.params_map = params_map
        self.params_map['all'].extend([
            'async_req',
            '_host_index',
            '_preload_content',
            '_request_timeout',
            '_return_http_data_only',
            '_check_input_type',
            '_check_return_type',
            '_content_type',
            '_spec_property_naming',
            '_request_auths'
        ])
        self.params_map['nullable'].extend(['_request_timeout'])
        self.validations = root_map['validations']
        self.allowed_values = root_map['allowed_values']
        self.openapi_types = root_map['openapi_types']
        extra_types = {
            'async_req': (bool,),
            '_host_index': (none_type, int),
            '_preload_content': (bool,),
            '_request_timeout': (none_type, float, (float,), [float], int, (int,), [int]),
            '_return_http_data_only': (bool,),
            '_check_input_type': (bool,),
            '_check_return_type': (bool,),
            '_spec_property_naming': (bool,),
            '_content_type': (none_type, str),
            '_request_auths': (none_type, list)
        }
        self.openapi_types.update(extra_types)
        self.attribute_map = root_map['attribute_map']
        self.location_map = root_map['location_map']
        self.collection_format_map = root_map['collection_format_map']
        self.headers_map = headers_map
        self.api_client = api_client
        self.callable = callable

    def __validate_inputs(self, kwargs):
        for param in self.params_map['enum']:
            if param in kwargs:
                check_allowed_values(
                    self.allowed_values,
                    (param,),
                    kwargs[param]
                )

        for param in self.params_map['validation']:
            if param in kwargs:
                check_validations(
                    self.validations,
                    (param,),
                    kwargs[param],
                    configuration=self.api_client.configuration
                )

        if kwargs['_check_input_type'] is False:
            return

        for key, value in kwargs.items():
            fixed_val = validate_and_convert_types(
                value,
                self.openapi_types[key],
                [key],
                kwargs['_spec_property_naming'],
                kwargs['_check_input_type'],
                configuration=self.api_client.configuration
            )
            kwargs[key] = fixed_val

    def __gather_params(self, kwargs):
        params = {
            'body': None,
            'collection_format': {},
            'file': {},
            'form': [],
            'header': {},
            'path': {},
            'query': []
        }

        for param_name, param_value in kwargs.items():
            param_location = self.location_map.get(param_name)
            if param_location is None:
                continue
            if param_location:
                if param_location == 'body':
                    params['body'] = param_value
                    continue
                base_name = self.attribute_map[param_name]
                if (param_location == 'form' and
                        self.openapi_types[param_name] == (file_type,)):
                    params['file'][base_name] = [param_value]
                elif (param_location == 'form' and
                        self.openapi_types[param_name] == ([file_type],)):
                    # param_value is already a list
                    params['file'][base_name] = param_value
                elif param_location in {'form', 'query'}:
                    param_value_full = (base_name, param_value)
                    params[param_location].append(param_value_full)
                if param_location not in {'form', 'query'}:
                    params[param_location][base_name] = param_value
                collection_format = self.collection_format_map.get(param_name)
                if collection_format:
                    params['collection_format'][base_name] = collection_format

        return params

    def __call__(self, *args, **kwargs):
        """ This method is invoked when endpoints are called
        Example:

        api_instance = ClusterAPIApi()
        api_instance.async_clustering_problem  # this is an instance of the class Endpoint
        api_instance.async_clustering_problem()  # this invokes api_instance.async_clustering_problem.__call__()
        which then invokes the callable functions stored in that endpoint at
        api_instance.async_clustering_problem.callable or self.callable in this class

        """
        return self.callable(self, *args, **kwargs)

    def call_with_http_info(self, **kwargs):

        try:
            index = self.api_client.configuration.server_operation_index.get(
                self.settings['operation_id'], self.api_client.configuration.server_index
            ) if kwargs['_host_index'] is None else kwargs['_host_index']
            server_variables = self.api_client.configuration.server_operation_variables.get(
                self.settings['operation_id'], self.api_client.configuration.server_variables
            )
            _host = self.api_client.configuration.get_host_from_settings(
                index, variables=server_variables, servers=self.settings['servers']
            )
        except IndexError:
            if self.settings['servers']:
                raise ApiValueError(
                    "Invalid host index. Must be 0 <= index < %s" %
                    len(self.settings['servers'])
                )
            _host = None

        for key, value in kwargs.items():
            if key not in self.params_map['all']:
                raise ApiTypeError(
                    "Got an unexpected parameter '%s'"
                    " to method `%s`" %
                    (key, self.settings['operation_id'])
                )
            # only throw this nullable ApiValueError if _check_input_type
            # is False, if _check_input_type==True we catch this case
            # in self.__validate_inputs
            if (key not in self.params_map['nullable'] and value is None
                    and kwargs['_check_input_type'] is False):
                raise ApiValueError(
                    "Value may not be None for non-nullable parameter `%s`"
                    " when calling `%s`" %
                    (key, self.settings['operation_id'])
                )

        for key in self.params_map['required']:
            if key not in kwargs.keys():
                raise ApiValueError(
                    "Missing the required parameter `%s` when calling "
                    "`%s`" % (key, self.settings['operation_id'])
                )

        self.__validate_inputs(kwargs)

        params = self.__gather_params(kwargs)

        accept_headers_list = self.headers_map['accept']
        if accept_headers_list:
            params['header']['Accept'] = self.api_client.select_header_accept(
                accept_headers_list)

        if kwargs.get('_content_type'):
            params['header']['Content-Type'] = kwargs['_content_type']
        else:
            content_type_headers_list = self.headers_map['content_type']
            if content_type_headers_list:
                if params['body'] != "":
                    content_types_list = self.api_client.select_header_content_type(
                        content_type_headers_list, self.settings['http_method'],
                        params['body'])
                    if content_types_list:
                        params['header']['Content-Type'] = content_types_list

        return self.api_client.call_api(
            self.settings['endpoint_path'], self.settings['http_method'],
            params['path'],
            params['query'],
            params['header'],
            body=params['body'],
            post_params=params['form'],
            files=params['file'],
            response_type=self.settings['response_type'],
            auth_settings=self.settings['auth'],
            async_req=kwargs['async_req'],
            _check_type=kwargs['_check_return_type'],
            _return_http_data_only=kwargs['_return_http_data_only'],
            _preload_content=kwargs['_preload_content'],
            _request_timeout=kwargs['_request_timeout'],
            _host=_host,
            _request_auths=kwargs['_request_auths'],
            collection_formats=params['collection_format'])
