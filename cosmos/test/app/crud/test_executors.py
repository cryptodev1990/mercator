import json
import pytest

from app.db import engine
from app.crud.executors import _prepare_args_for_area_near_constraint, area_near_constraint, x_in_y

def test__prepare_args_for_area_near_constraint():
    """Test _prepare_args_for_area_near_constraint."""
    args = {
        'named_place_or_amenity_0': 'San Francisco',
        'distance_or_time_0': '500m',
        'named_place_or_amenity_1': 'Sacre Coeur',
        'distance_or_time_1': '250m',
    }
    res = _prepare_args_for_area_near_constraint(args)
    assert len(res) == 2
    assert res[0].entity.lookup == 'San Francisco'
    assert res[0].distance_in_meters == 500
    assert res[1].entity.lookup == 'Sacre Coeur'
    assert res[1].distance_in_meters == 250

    # Test kwargs
    args = {
        'named_place_or_amenity_0': 'San Francisco',
        'distance_or_time_0': '500m',
        'named_place_or_amenity_1': 'Sacre Coeur',
        'distance_or_time_1': '250m',
        'named_place_or_amenity_2': 'Sacre Coeur',
        'distance_or_time_2': '250m',
    }
    res = _prepare_args_for_area_near_constraint(args)
    assert len(res) == 3
    assert res[2].entity.lookup == 'Sacre Coeur'
    assert res[2].distance_in_meters == 250


def test__prepare_args_for_area_near_constraint_bad_inputs():
    """Test _prepare_args_for_area_near_constraint."""

    # Test missing distance or time
    try:
        args = {
            'named_place_or_amenity_0': 'San Francisco',
            'named_place_or_amenity_1': 'Sacre Coeur',
            'distance_or_time_1': '250m',
        }
        res = _prepare_args_for_area_near_constraint(args)
    except ValueError as e:
        assert str(e) == "Number of elements mismatched"
    
    try:
        args = {
            'named_place_or_amenity_0': 'San Francisco',
            'distance_or_time_0': '20 minutes',
            'named_place_or_amenity_0': 'Sacramento',
            'distance_or_time_0': '500m',
        }
        res = _prepare_args_for_area_near_constraint(args)
    except NotImplementedError as e:
        assert str(e) == "Time is not yet supported"

    # Test mismatched args
    try:
        args = {
            'named_place_or_amenity_0': 'San Francisco',
            'distance_or_time_0': '500m',
            'named_place_or_amenity_2': 'Sacre Coeur',
            'distance_or_time_3': '250m',
        }
        res = _prepare_args_for_area_near_constraint(args)
    except AssertionError as e:
        assert str(e) == "Missing a distance or time"


    # Test invalid key
    try:
        args = {
            'banana_stand_0': 'San Francisco',
            'banana_stand_1': 'San Francisco',
            'named_place_or_amenity_0': 'Sacre Coeur',
            'distance_or_time_0': '500m',
            'named_place_or_amenity_1': 'Sacre Coeur',
            'distance_or_time_1': '250m',
        }
    except AssertionError as e:
        assert str(e) == "Invalid key, can only start with named_place_or_amenity_ or distance_or_time_"
    

@pytest.mark.asyncio
async def test_area_near_constaint_named_places():
    async with engine.begin() as conn:
        happy_case = await area_near_constraint(
            named_place_or_amenity_0='San Francisco',
            distance_or_time_0='25 mi',
            named_place_or_amenity_1='Antioch CA',
            distance_or_time_1='25 mi',
            named_place_or_amenity_2='San Jose CA',
            distance_or_time_2='25 mi',
            conn=conn
        )
        assert happy_case.entities[0].lookup == 'San Francisco'
        assert happy_case.entities[0].matched_geo_ids == ['111968']
        assert happy_case.entities[1].lookup == 'Antioch CA'
        assert happy_case.entities[1].matched_geo_ids == ['3705567']
        assert happy_case.entities[2].lookup == 'San Jose CA'
        assert happy_case.entities[2].matched_geo_ids == ['112143']

        OVERLAP = {'type': 'Polygon', 'coordinates': [[[-122.244965542, 37.787081058], [-122.237297836, 37.790296028], [-122.237032931, 37.790397755], [-122.207963557, 37.800581681], [-122.207690407, 37.800668454], [-122.177573078, 37.80927286], [-122.177292903, 37.809344171], [-122.146729143, 37.816199084], [-122.146443266, 37.816254726], [-122.115148613, 37.821428185], [-122.114858559, 37.821467754], [-122.10450138, 37.822673825], [-122.104520998, 37.822778523], [-122.094628541, 37.823944428], [-122.085920228, 37.824902258], [-122.08537976, 37.824957486], [-122.053652585, 37.827306884], [-122.053108454, 37.827331968], [-122.042895838, 37.827517833], [-122.033235718, 37.828389292], [-122.033126793, 37.828396017], [-122.001481041, 37.829472449], [-122.001371911, 37.829473145], [-121.985927503, 37.8291461], [-121.958275663, 37.831606261], [-121.958053586, 37.831611168], [-121.882085468, 37.828241328], [-121.881865337, 37.828216796], [-121.850054716, 37.822472438], [-121.840249685, 37.801853888], [-121.825752362, 37.729045948], [-121.830101885, 37.655414286], [-121.853063931, 37.583999064], [-121.864517744, 37.565296675], [-121.871902976, 37.565910244], [-121.878314092, 37.566973426], [-121.979573439, 37.593880558], [-121.986972905, 37.596645878], [-121.991870198, 37.598383726], [-121.996477444, 37.600455183], [-122.024482053, 37.609557715], [-122.027868398, 37.61089725], [-122.099235893, 37.645944793], [-122.16139686, 37.690762723], [-122.212250965, 37.743850047], [-122.219971839, 37.756022536], [-122.231095534, 37.766699917], [-122.244965542, 37.787081058]]]}
        assert json.dumps(happy_case.geom.features[0].geometry.coordinates[0]) == json.dumps(OVERLAP['coordinates'])
        assert len(happy_case.geom.features) == 1


@pytest.mark.skip(reason="Need to implement")
@pytest.mark.asyncio
async def test_area_near_constaint_categories():
    async with engine.begin() as conn:
        happy_case = await area_near_constraint(
            named_place_or_amenity_0='grocery stores',
            distance_or_time_0='5 mi',
            named_place_or_amenity_1='schools',
            distance_or_time_1='5 mi',
            named_place_or_amenity_2='parks',
            distance_or_time_2='5 mi',
            named_place_or_amenity_3='hospitals',
            distance_or_time_3='5 mi',
            conn=conn
        )
        # TBD
        assert happy_case.entities[0].lookup == ''

        OVERLAP = {'type': 'Polygon', 'coordinates': [[[-122.244965542, 37.787081058], [-122.237297836, 37.790296028], [-122.237032931, 37.790397755], [-122.207963557, 37.800581681], [-122.207690407, 37.800668454], [-122.177573078, 37.80927286], [-122.177292903, 37.809344171], [-122.146729143, 37.816199084], [-122.146443266, 37.816254726], [-122.115148613, 37.821428185], [-122.114858559, 37.821467754], [-122.10450138, 37.822673825], [-122.104520998, 37.822778523], [-122.094628541, 37.823944428], [-122.085920228, 37.824902258], [-122.08537976, 37.824957486], [-122.053652585, 37.827306884], [-122.053108454, 37.827331968], [-122.042895838, 37.827517833], [-122.033235718, 37.828389292], [-122.033126793, 37.828396017], [-122.001481041, 37.829472449], [-122.001371911, 37.829473145], [-121.985927503, 37.8291461], [-121.958275663, 37.831606261], [-121.958053586, 37.831611168], [-121.882085468, 37.828241328], [-121.881865337, 37.828216796], [-121.850054716, 37.822472438], [-121.840249685, 37.801853888], [-121.825752362, 37.729045948], [-121.830101885, 37.655414286], [-121.853063931, 37.583999064], [-121.864517744, 37.565296675], [-121.871902976, 37.565910244], [-121.878314092, 37.566973426], [-121.979573439, 37.593880558], [-121.986972905, 37.596645878], [-121.991870198, 37.598383726], [-121.996477444, 37.600455183], [-122.024482053, 37.609557715], [-122.027868398, 37.61089725], [-122.099235893, 37.645944793], [-122.16139686, 37.690762723], [-122.212250965, 37.743850047], [-122.219971839, 37.756022536], [-122.231095534, 37.766699917], [-122.244965542, 37.787081058]]]}
        assert json.dumps(happy_case.geom.features[0].geometry.coordinates[0]) == json.dumps(OVERLAP['coordinates'])
        assert len(happy_case.geom.features) == 1



@pytest.mark.asyncio
async def test_x_in_y():
    async with engine.begin() as conn:
        happy_case = await x_in_y(
            needle_place_or_amenity="irish pub",
            haystack_place_or_amenity="san francisco",
            conn=conn
        )
        fc = {"type": "FeatureCollection", "features": [ { "type": "Feature", "id": "2249504566", "properties": { "tags": { "food": "yes", "name": "Irish Bank", "email": "theirishbank@yahoo.com", "phone": "+1 415 7887152", "amenity": "pub", "smoking": "no", "website": "https://www.theirishbank.com/", "addr:city": "San Francisco", "addr:state": "CA", "addr:street": "Mark Lane", "opening_hours": "Su,Mo,Tu 11:30-23:00; We,Th 11:30-00:00; Fr,Sa 11:30-02:00", "outdoor_seating": "yes", "addr:housenumber": "10", "contact:facebook": "The-Irish-Bank-57687294378", "contact:instagram": "irishbank", "opening_hours:url": "https://www.theirishbank.com", "opening_hours:kitchen": "Mo-Su 11:30-22:45" }, "osm_id": 2249504566 }, "geometry": { "type": "Point", "coordinates": [ -122.404722, 37.7904363 ] }, "bbox": None }, { "type": "Feature", "id": "61692712", "properties": { "tags": { "name": "Irish Times", "phone": "+1 800 800 8008", "amenity": "pub", "old_name": "Norton's Vault", "wheelchair": "no", "addr:street": "Sacramento Street", "indoor_seating": "yes", "outdoor_seating": "yes", "addr:housenumber": "500" }, "osm_id": 61692712 }, "geometry": { "type": "Point", "coordinates": [ -122.4015526, 37.7940403 ] }, "bbox": None }, { "type": "Feature", "id": "366723771", "properties": { "tags": { "name": "O'Reilly's Irish Pub & Restaurant", "amenity": "pub", "addr:street": "Green Street", "addr:housenumber": "622" }, "osm_id": 366723771 }, "geometry": { "type": "Point", "coordinates": [ -122.4097652, 37.7995333 ] }, "bbox": None }, { "type": "Feature", "id": "371251931", "properties": { "tags": { "name": "Kennedy's Irish Pub & Curry House", "amenity": "pub", "cuisine": "indian", "website": "kennedyscurry.com", "addr:street": "Columbus Avenue", "addr:housenumber": "1040" }, "osm_id": 371251931 }, "geometry": { "type": "Point", "coordinates": [ -122.4153272, 37.8041003 ] }, "bbox": None }, { "type": "Feature", "id": "264371921", "properties": { "tags": { "name": "Michael Collins Irish Bar", "height": "7", "amenity": "pub", "website": "https://www.facebook.com/michaelcollinshaight/", "building": "yes", "addr:street": "Haight Street", "opening_hours": "Mo-Sa 00:00-02:00,11:00-24:00; Su 00:00-02:00,09:00-24:00", "addr:housenumber": "1568" }, "osm_id": 264371921 }, "geometry": { "type": "Polygon", "coordinates": [ [ [ -122.4482159, 37.7703207 ], [ -122.4481615, 37.7700433 ], [ -122.4481447, 37.7699585 ], [ -122.4481433, 37.7699496 ], [ -122.4480473, 37.7699614 ], [ -122.4480702, 37.7700783 ], [ -122.448076, 37.770108 ], [ -122.4480792, 37.7701245 ], [ -122.4481066, 37.7702646 ], [ -122.4481202, 37.7702629 ], [ -122.4481335, 37.7703308 ], [ -122.4482159, 37.7703207 ] ] ] }, "bbox": None }, { "type": "Feature", "id": "264371921", "properties": { "tags": { "name": "Michael Collins Irish Bar", "height": "7", "amenity": "pub", "website": "https://www.facebook.com/michaelcollinshaight/", "building": "yes", "addr:street": "Haight Street", "opening_hours": "Mo-Sa 00:00-02:00,11:00-24:00; Su 00:00-02:00,09:00-24:00", "addr:housenumber": "1568" }, "osm_id": 264371921 }, "geometry": { "type": "LineString", "coordinates": [ [ -122.4480473, 37.7699614 ], [ -122.4481433, 37.7699496 ], [ -122.4481447, 37.7699585 ], [ -122.4481615, 37.7700433 ], [ -122.4482159, 37.7703207 ], [ -122.4481335, 37.7703308 ], [ -122.4481202, 37.7702629 ], [ -122.4481066, 37.7702646 ], [ -122.4480792, 37.7701245 ], [ -122.448076, 37.770108 ], [ -122.4480702, 37.7700783 ], [ -122.4480473, 37.7699614 ] ] }, "bbox": None }, { "type": "Feature", "id": "808930729", "properties": { "tags": { "food": "yes", "name": "Johnny Foley's Irish House", "phone": "+1 415 9540777", "theme": "irish", "amenity": "pub", "cuisine": "irish", "website": "https://www.johnnyfoleys.com/", "addr:city": "San Francisco", "mapillary": "501873397835113", "addr:state": "CA", "addr:street": "O'Farrell Street", "survey:date": "2020-01-20", "contact:yelp": "https://www.yelp.com/biz/johnny-foleys-san-francisco", "addr:postcode": "94102", "opening_hours": "We,Th,Fr 17:00-22:00+; Sa,Su 11:00-22:00+; Mo,Tu off", "addr:housenumber": "243", "contact:facebook": "johnnyfoleysirishhouse", "contact:instagram": "johnnyfoleysirishhouse" }, "osm_id": 808930729 }, "geometry": { "type": "Point", "coordinates": [ -122.408751, 37.7862372 ] }, "bbox": None }, { "type": "Feature", "id": "621179351", "properties": { "tags": { "food": "yes", "name": "The Chieftain Irish Pub & Restaurant", "email": "info@thechieftain.com", "phone": "+1 415 6150916", "amenity": "pub", "cuisine": "burger;wings;fish_and_chips;irish", "website": "https://www.thechieftain.com/", "addr:city": "San Francisco", "addr:state": "CA", "addr:street": "5th Street", "addr:country": "US", "website:menu": "https://www.thechieftain.com/menus/", "addr:postcode": "94103", "opening_hours": "Fr-Su 12:00+; Mo,Tu,We 16:00+; Th 11:00+", "contact:twitter": "ChieftainPubSF", "addr:housenumber": "198", "contact:facebook": "chieftainirishpubsf", "contact:instagram": "Chieftainpubsf", "opening_hours:url": "https://www.thechieftain.com/location/the-chieftain/", "contact:tripadvisor": "https://www.tripadvisor.com/Restaurant_Review-g60713-d537705-Reviews-The_Chieftain_Irish_Pub_Restaurant-San_Francisco_California.html" }, "osm_id": 621179351 }, "geometry": { "type": "Point", "coordinates": [ -122.4052119, 37.7814985 ] }, "bbox": None } ], "bbox": None }
        assert happy_case.geom.json() == json.dumps(fc)
        assert len(happy_case.geom.features) == 8