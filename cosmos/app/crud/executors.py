"""
NOTE: Currently, all functions in this file are used as executors for intents and their signatures are used by OpenAI.

**If you change a function signature, you must also change the corresponding intent in intents.yaml**

This will change when we actually have more users
"""
from pydoc import resolve
from typing import Dict, List
import jinja2
import json
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import text
from app.core.datatypes import Feature, FeatureCollection, MultiPolygon, Polygon
from app.crud import entity_resolve
from app.crud.entity_resolve import resolve_entity
from app.gateways.geo_route import multiple_concurrent_routes
from app.parsers.entity_resolvers import Time, parse_into_meters, parse_into_seconds
from app.schemas import BufferedEntity, ExecutorResponse, ParsedEntity

MAX_SIMULTANEOUS_ISOCHRONES = 100
GENERATED_SHAPE_ID = -1

def _extract_first_geom(er: ExecutorResponse) -> Feature:
    feature_collection = er.geom
    if len(feature_collection.features) == 0:
        raise ValueError("No features found")
    return feature_collection.features[0]

def _prepare_args_for_area_near_constraint(collective_dict: Dict) -> List[BufferedEntity]:
    for k, v in collective_dict.items():
        if k.startswith('distance_or_time_'):
            try:
                t = parse_into_seconds(v)
                if t is not None:
                    raise NotImplementedError("Time is not supported yet")
            except ValueError:
                pass
            try:
                collective_dict[k] = parse_into_meters(v, 100)
            except ValueError:
                raise ValueError(f"Could not parse {v} into meters")
        if k.startswith('named_place_or_amenity_'):
            if v == "":
                raise ValueError("Missing a named place or amenity")

    num_pairs = int(len(collective_dict) / 2)
    if len(collective_dict) % 2 != 0:
        raise ValueError("Number of elements mismatched")
    if num_pairs > 16:
        raise ValueError("Too many elements")

    # assert that each pair has a named_place_or_amenity and a distance_or_time
    for i in range(num_pairs):
        assert f"named_place_or_amenity_{i}" in collective_dict and f"distance_or_time_{i}" in collective_dict, "Missing a distance or time"

    # assert that each key either starts with named_place_or_amenity_ or distance_or_time_
    assert all([k.startswith('named_place_or_amenity_') or k.startswith('distance_or_time_') for k in collective_dict.keys()]), "Invalid key, can only start with named_place_or_amenity_ or distance_or_time_"

    records = []
    items = [x for x in collective_dict.values()]
    for i in range(0, len(items), 2):
        records.append(BufferedEntity(
            entity=resolve_entity(items[i]),
            distance_in_meters=items[i + 1]
        ))
    return records


async def area_near_constraint(
    named_place_or_amenity_0: str,
    distance_or_time_0: str,
    named_place_or_amenity_1: str,
    distance_or_time_1: str,
    conn: AsyncConnection,
    **kwargs
) -> ExecutorResponse:
    """
    Parse examples

    Within 500m of a public school and 200m of a coffee shop -> area_near_constraint("public school", "500m", "coffee shop", "200m")
    area 100m from the blue bottle on market and 200m from Twitter HQ and within 1 mile of dolores park -> area_near_constraint("blue bottle on market", "100m", "Twitter HQ", "200m", "dolores park", "1 mile")
    100m of a storefront and 10m of a bike lane -> area_near_constraint("storefront", "100m", "bike lane", "10m")
    20 ft of a bus stop, 100m of a park, and 500m of a hospital -> area_near_constraint("bus stop", "20 ft", "park", "100m", "hospital", "500m")
    Near a bus stop, 100m of a park, and 500m of a hospital -> area_near_constraint("bus stop", "", "park", "100m", "hospital", "500m)
    Near a school, near a park, and near a hospital -> area_near_constraint("school", "", "park", "", "hospital", "")
    20 mi of a pinball machine, about 50 minutes of a bowling alley, and within 20 feet from a bar -> area_near_constraint("pinball machine", "20 mi", "bowling alley", "50 minutes", "bar", "20 feet")
    within 10 miles of Palo Alto and San Francisco -> area_near_constraint("Palo Alto", "10 miles", "San Francisco", "10 miles")
    """
    collective_dict = {
        "named_place_or_amenity_0": named_place_or_amenity_0,
        "distance_or_time_0": distance_or_time_0,
        "named_place_or_amenity_1": named_place_or_amenity_1,
        "distance_or_time_1": distance_or_time_1,
    }
    assert all([k.startswith('named_place_or_amenity_') or k.startswith('distance_or_time_') for k in kwargs.keys()])
    collective_dict = {**collective_dict, **kwargs}
    records = _prepare_args_for_area_near_constraint(collective_dict)
    query = jinja2.Template("""
    WITH t1 AS (
    {% for rec in records %}
    SELECT ST_Union(ST_Buffer(geom::GEOGRAPHY, {{ rec.distance_in_meters }})::GEOMETRY) AS geom_buff
    FROM
      osm
    JOIN (
            {# If the entity was resolved by the entity resolver, use the matched geo ids #}
            {% if rec.entity.match_type != "raw_lookup" %}
                SELECT UNNEST('{ {{ rec.entity.matched_geo_ids | join(',') }} }'::BIGINT []) AS osm_id
            {% else %}
                {# Otherwise, use the raw text lookup #}
                SELECT osm_id
                FROM
                    osm,
                    plainto_tsquery( '{{ rec.entity.lookup }}' ) query,
                    similarity('{{ rec.entity.lookup }}', tags_text) similarity
                WHERE TRUE
                    WEBSEARCH_TO_TSQUERY( '{{ rec.entity.lookup }}' ) query
                WHERE 1=1
                    AND query @@ fts
                LIMIT 100000
            {% endif %}
    ) queried ON queried.osm_id = osm.osm_id
    WHERE 1=1
        {# Stack the results set #}
        {% if not loop.last %}UNION ALL{% endif %}
    {% endfor %}
    )
    , unioned AS (
        SELECT ST_Union(geom_buff) AS geom_buff
        FROM t1
    )
    -- Get the intersection of all the geometries
    , hollow AS (
      SELECT ST_Union(ST_MakeValid(ST_Difference(a.geom_buff, b.geom_buff))) AS geom_buff
      FROM unioned a, t1 b
      WHERE 1=1
        AND ST_Intersects(a.geom_buff, b.geom_buff)
    )

    SELECT ST_AsGeoJSON(ST_Difference(unioned.geom_buff, hollow.geom_buff)) AS geojson
    FROM unioned
    CROSS JOIN hollow
    ;
    """).render(records=records)
    res = (await conn.execute(text(query))).fetchone()
    if res is None:
        raise ValueError("No results found")
    # Format as geojson polygon
    res = json.loads(res[0])
    multipolygon = MultiPolygon(type="MultiPolygon", coordinates=[res['coordinates']] if res['type'] == 'Polygon' else res['coordinates'])
    return ExecutorResponse(
        geom=FeatureCollection(
            type="FeatureCollection",
            features=[
                Feature(
                    id=GENERATED_SHAPE_ID,
                    type="Feature",
                    geometry=multipolygon,
                    properties={},
                )
            ],
        ),
        entities=[
            ParsedEntity(**rec.entity.__dict__) for rec in records
        ],
    )


async def raw_lookup(search_term: str, conn: AsyncConnection):
    # TODO need to enable known_category lookup
    searched_entity = resolve_entity(search_term, ["raw_lookup"])
    query = jinja2.Template("""
    SELECT JSON_BUILD_OBJECT(
        'type', 'FeatureCollection',
        'features', JSON_AGG(
            JSON_BUILD_OBJECT(
                'type', 'Feature',
                'id', osm.osm_id,
                'geometry', ST_AsGeoJSON(geom)::JSON,
                'properties', tags
            )
        )
    ) AS feature_collection
    FROM
      osm
    JOIN (
            {% if needle.match_type != "raw_lookup" %}
                SELECT UNNEST('{ {{ needle.matched_geo_ids | join(',') }} }'::BIGINT []) AS osm_id
            {% else %}
                {# Otherwise, use the raw text lookup #}
                SELECT osm_id
                FROM
                    osm,
                    plainto_tsquery( '{{ needle.lookup }}' ) query
                WHERE 1=1
                    AND query @@ fts
                LIMIT 100000
            {% endif %}
    ) queried ON queried.osm_id = osm.osm_id
    """).render(needle=searched_entity)
    geojson = (await conn.execute(text(query))).scalar()
    if geojson is None:
        raise ValueError("No results found")
    return ExecutorResponse(
        geom=geojson,  # type: ignore
        entities=[ParsedEntity(**searched_entity.__dict__)],
    )


async def x_within_time_or_distance_of_y(
    named_place_or_amenity_0: str,
    distance_or_time: str,
    named_place_or_amenity_1: str,
    conn: AsyncConnection
):
    """
    Parse examples

    All the coffee shops within 500m of a public school -> x_within_time_or_distance_of_y("coffee shop", "500m", "public school")
    All the bike lanes within 10m of a storefront -> x_within_time_or_distance_of_y("bike lane", "10m", "storefront")
    bars within 20 minutes of Alamo Square Park -> x_within_time_or_distance_of_y("bar", "20 minutes", "alamo square park")
    convenience store within a 20 minute drive of 1455 Market St -> x_within_time_or_distance_of_y("convenience store", "20 minute", "1455 Market St")
    ATMs within 10 minutes of a gas station -> x_within_time_or_distance_of_y("ATM", "20 minutes", "gas station")
    """

    try:
        Time(distance_or_time)
        # get all entities that belong to the consequent
        res = (await conn.execute(text("""
            SELECT COUNT(*) AS num_rows
            FROM
                osm,
                plainto_tsquery(:named_place_or_amenity_0) query,
                similarity(:named_place_or_amenity_0, tags_text) similarity
            WHERE 1=1
                AND query @@ fts
                AND similarity > 0.01
        """), {"named_place_or_amenity_0": named_place_or_amenity_0})).fetchone()
        if res is None:
            return None
        num_rows = res["num_rows"]  # type: ignore
        if num_rows > MAX_SIMULTANEOUS_ISOCHRONES:
            raise ValueError("Too many rows, narrow down search")
        # get all entities that belong to the consequent
        res = await conn.execute(text("""
        -- build a geosjon feature collection
        SELECT JSONB_BUILD_OBJECT(
            'type', 'FeatureCollection',
            'features', jsonb_agg(feature)
        )
        FROM (
            SELECT JSONB_BUILD_OBJECT(
                'type', 'Feature',
                'id', osm_id,
                'geometry', ST_AsGeoJSON(geom)::JSONB,
                'properties', JSONB_BUILD_OBJECT(
                    'osm_id', osm_id,
                    'tags', tags
                )
            ) AS feature
            FROM
                osm,
                plainto_tsquery(:named_place_or_amenity_1) query,
                similarity(:named_place_or_amenity_1, tags_text) similarity
            WHERE 1=1
                AND query @@ fts
                AND similarity > 0.01
            ORDER BY
                TS_RANK_CD(fts, query) DESC,
                similarity DESC
        ) AS features
        LIMIT 50
        """), {"named_place_or_amenity_1": named_place_or_amenity_1})
        res = res.fetchall()
    except ValueError:
        pass

    geom_with_entities = await area_near_constraint(
        named_place_or_amenity_0,
        '5m',
        named_place_or_amenity_1,
        distance_or_time,
        conn=conn
    )

    geom = _extract_first_geom(geom_with_entities)

    res = await conn.execute(text("""
    -- build a geosjon feature collection
    SELECT JSONB_BUILD_OBJECT(
        'type', 'FeatureCollection',
        'features', jsonb_agg(feature)
    )
    FROM (
        SELECT JSONB_BUILD_OBJECT(
            'type', 'Feature',
            'id', osm_id,
            'geometry', ST_AsGeoJSON(geom)::JSONB,
            'properties', JSONB_BUILD_OBJECT(
                'osm_id', osm_id,
                'tags', tags
            )
        ) AS feature
      FROM
          osm,
          plainto_tsquery(:search_term) query,
          similarity(:search_term, tags_text) similarity
      WHERE 1=1
          AND ST_Intersects(geom, ST_GeomFromGeoJSON(:geom_buff))
          AND query @@ fts
          AND similarity > 0.01
      ORDER BY
          TS_RANK_CD(fts, query) DESC,
          similarity DESC
        LIMIT 100000
    ) AS features
    """), {
        "geom_buff": geom,
        "search_term": named_place_or_amenity_0,
    })
    res = res.fetchall()
    return res


async def x_in_y(
    needle_place_or_amenity: str,
    haystack_place_or_amenity: str,
    conn: AsyncConnection
) -> ExecutorResponse:
    """
    Parse examples

    San Francisco public schools -> x_in_y("public schools", "San Francisco")
    California coffee shops -> x_in_y("coffee shops", "California")
    zoos in Dayton, Ohio -> x_in_y("zoos", "Dayton, Ohio")
    Bethesda Maryland urgent care facilities -> x_in_y("urgent care facilities", "Bethesda Maryland")
    shopping in Honolulu HI -> x_in_y("shopping", "Honolulu HI")
    food deserts in the 512 area code -> x_in_y("food deserts", "512 area code")
    """
    needle = resolve_entity(needle_place_or_amenity, enabled=["known_category", "raw_lookup"])
    haystack = resolve_entity(haystack_place_or_amenity, enabled=["named_place"])  # Make sure it's a named place
    res = await conn.execute(text(jinja2.Template("""
        SELECT JSONB_BUILD_OBJECT(
            'type', 'FeatureCollection',
            'features', jsonb_agg(feature)
        )
        FROM (
          SELECT JSONB_BUILD_OBJECT(
              'type', 'Feature',
              'id', osm_id,
              'geometry', ST_AsGeoJSON(geom)::JSONB,
              'properties', JSONB_BUILD_OBJECT(
                  'osm_id', osm_id,
                  'tags', tags
              )
          ) AS feature
          FROM
              osm
          WHERE 1=1
              AND osm_id IN (
                {{ needle.sql_snippet }}
              )
              AND ST_Intersects(geom,
               (
                  SELECT geom AS container_geom
                  FROM
                    osm
                  WHERE 1=1
                    AND (tags ? 'place' OR tags ? 'boundary')
                    AND osm_id IN (
                        {{ haystack.matched_geo_ids | join(",")}}
                    )
                  GROUP BY 1
                  ORDER BY ST_Area(geom) DESC
                  LIMIT 1
               ))
        ) AS features
    """).render({"needle": needle, "haystack": haystack})))
    feature_collection = res.fetchone()[0]  # type: ignore
    return ExecutorResponse(
        geom=feature_collection,
        entities=[ParsedEntity(**needle.__dict__), ParsedEntity(**haystack.__dict__)],
    )


async def x_near_y(
    named_place_or_amenity_0: str,
    named_place_or_amenity_1: str,
    conn: AsyncConnection
):
    """
    Parse examples

    """
    pass


async def x_between_y_and_z(
    named_place_or_amenity_0: str,
    named_place_or_amenity_1: str,
    named_place_or_amenity_2: str,
    conn: AsyncConnection
):
    """
    Parse examples

    Gas stations from San Francisco to Peoria -> x_between_y_and_z("gas stations", "San Francisco", "Peoria")
    Amusement parks along the way from Austin to Miami -> x_between_y_and_z("amusement parks", "Austin", "Miami")
    Parks along the way from Miami to Austin -> x_between_y_and_z("parks", "Miami", "Austin")
    Businesses along the way from coffee shops to Bethesda Maryland urgent care facilities -> x_between_y_and_z("businesses", "coffee shops", "Bethesda Maryland urgent care facilities")
    restaurants between Alamo Square and Crissy Fields -> x_between_y_and_z("restaurants", "Alamo Square", "Crissy Fields")
    Apple stores on the route to San Jose from San Francisco -> x_between_y_and_z("Apple stores", "San Francisco", "San Jose")
    Find the rest stops between Exit 3 and Exit 40 on I-80 -> x_between_y_and_z("rest stops", "Exit 3", "Exit 40")
    """
    # Get the locations of all three places
    res = await conn.execute(text("""
        WITH a AS (
        SELECT
            ST_Centroid(geom) AS center_geom
            , osm_id
        FROM
            osm,
            WEBSEARCH_TO_TSQUERY(:anterior) query,
            SIMILARITY(:anterior, tags_text) similarity
        WHERE 1=1
            AND query @@ fts
            AND similarity > 0.01
            AND geom IS NOT NULL
            LIMIT 5
        )
        , p AS (
        SELECT
            ST_Centroid(geom) AS center_geom
            , osm_id
        FROM
            osm,
            WEBSEARCH_TO_TSQUERY(:posterior) query,
            SIMILARITY(:posterior, tags_text) similarity
        WHERE 1=1
            AND query @@ fts
            AND similarity > 0.01
            AND geom IS NOT NULL
            LIMIT 5
        )
        SELECT ST_X(a.center_geom) AS anterior_x
        , ST_Y(a.center_geom) AS anterior_y
        , ST_X(p.center_geom) AS posterior_x
        , ST_Y(p.center_geom) AS posterior_y
        , a.osm_id AS anterior_osm_id
        , p.osm_id AS posterior_osm_id
        FROM a
        CROSS JOIN p
    """), {"anterior": named_place_or_amenity_1, "posterior": named_place_or_amenity_2})
    if not res:
        return []
    rows = res.fetchall()  # type: ignore
    if not rows:
        return []
    routes_list = []
    for row in rows:  # type: ignore
        assert row[0] is not None, "anterior_x is None when it should have a value"
        routes_list.append([
            row[0],
            row[1],
            row[2],
            row[3],
        ])
    routes = await multiple_concurrent_routes(routes_list)
    for i, route in enumerate(routes):
        route['anterior_osm_id'] = rows[i][4]  # type: ignore
        route['posterior_osm_id'] = rows[i][5]  # type: ignore
    res = await conn.execute(text(jinja2.Template("""
    WITH decoded_routes AS (
        {% for route in routes %}
        {% if route.get('paths') and route.get('paths')[0].get('points') %}
        SELECT
        {{ route.get('anterior_osm_id') }} AS anterior_osm_id
        , {{ route.get('posterior_osm_id') }} AS posterior_osm_id
        , ST_Buffer(ST_LineFromEncodedPolyline('{{ route.get('paths')[0].get('points') }}')::GEOGRAPHY, 200)::GEOMETRY AS geom
        {% endif %}
        {% if not loop.last %} UNION ALL {% endif %}
        {% endfor %}
    )
    , unioned_routes AS (
        SELECT
          ST_UNION(geom) AS unioned_geom
        FROM decoded_routes
    )
    , objects AS (
    SELECT
        geom
        , osm_id
        , tags
    FROM
        osm
    JOIN unioned_routes ON ST_Intersects(geom, unioned_geom)
    WHERE 1=1
        AND WEBSEARCH_TO_TSQUERY(:interior) @@ fts
    )
    SELECT JSONB_BUILD_OBJECT(
        'type', 'FeatureCollection',
        'features', jsonb_agg(feature)
    )
    FROM (
      SELECT JSONB_BUILD_OBJECT(
          'type', 'Feature',
          'id', osm_id,
          'geometry', ST_AsGeoJSON(geom)::JSONB,
          'properties', JSONB_BUILD_OBJECT(
              'osm_id', osm_id,
              'tags', tags
          )
      ) AS feature
      FROM (
        SELECT geom, osm_id, tags FROM objects
        UNION ALL
        SELECT geom
        , -1 AS osm_id
        , JSONB_BUILD_OBJECT('anterior_osm_id', anterior_osm_id, 'posterior_osm_id', posterior_osm_id) AS tags
        FROM decoded_routes
      ) AS subfeatures
    ) features;
    """).render(routes=routes)), {"interior": named_place_or_amenity_0})
    geoms = res.fetchone()[0] if res else []  # type: ignore
    return geoms
