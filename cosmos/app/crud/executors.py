"""
NOTE: Currently, all functions in this file are used as executors for intents and their signatures are used by OpenAI.

**If you change a function signature, you must also change the corresponding intent in intents.yaml**

This will change when we actually have more users
"""
from typing import Dict, List
import jinja2
import json
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import text
from app.core.datatypes import Feature, FeatureCollection, MultiPolygon
from app.crud.entity_resolve import named_place, resolve_entity
from app.gateways.geo_route import get_route, multiple_concurrent_routes, route
from app.parsers.entity_resolvers import Time, parse_into_meters, parse_into_seconds
from app.schemas import Distance, ExecutorResponse, NamedPlaceParsedEntity, ParsedEntity

def _prep_geoids(geoids: List[str]) -> str:
    return ','.join(['\'%s\'' % x for x in geoids])


def surround_by_quote(a_list):
    return ['"%s"' % an_element for an_element in a_list]


MAX_SIMULTANEOUS_ISOCHRONES = 100
GENERATED_SHAPE_ID = -1

def _extract_first_geom(er: ExecutorResponse) -> Feature:
    feature_collection = er.geom
    if len(feature_collection.features) == 0:
        raise ValueError("No features found")
    return feature_collection.features[0]

def _prepare_args_for_area_near_constraint(collective_dict: Dict) -> List[ParsedEntity]:
    for k, v in collective_dict.items():
        if k.startswith('distance_or_time_'):
            if isinstance(v, Distance):
                collective_dict[k] = v.m
                continue
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
        res_ent = resolve_entity(items[i])
        records.append(ParsedEntity(
            lookup=res_ent.lookup,
            match_type=res_ent.match_type,
            geoids=res_ent.geoids,
            m=items[i + 1]
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
    SELECT ST_Union(ST_Buffer(geom::GEOGRAPHY, {{ rec.m }})::GEOMETRY) AS geom_buff
    FROM
      osm
    JOIN (
            {# If the entity was resolved by the entity resolver, use the matched geo ids #}
            {% if rec.match_type == "named_place" %}
                SELECT UNNEST('{ {{ rec.geoids | join(',') }} }'::VARCHAR []) AS id
            {% elif rec.match_type == "category" %}
                SELECT osm_id AS id
                FROM category_membership
                WHERE 1=1
                    -- TODO how should we really do this?
                  AND human_readable ILIKE '%{{ rec.lookup }}%'
                LIMIT 100000
            {% elif rec.match_type == "fuzzy" %}
                {# Otherwise, use the raw text lookup #}
                SELECT id
                FROM
                    osm,
                    plainto_tsquery( '{{ rec.lookup }}' ) query
                WHERE 1=1
                    AND query @@ fts
                LIMIT 100000
            {% endif %}
    ) queried ON queried.id = osm.id
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
    , ST_Area(ST_Difference(unioned.geom_buff, hollow.geom_buff), FALSE) AS area
    FROM unioned
    CROSS JOIN hollow
    ;
    """).render(records=records)
    res = (await conn.execute(text(query))).fetchone()
    if res is None:
        raise ValueError("No results found")
    # Format as geojson polygon
    area = res[1]
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
                    properties={
                        "area": area,
                    },
                )
            ],
        ),
        entities=[
            ParsedEntity(**rec.__dict__) for rec in records
        ],
    )


async def raw_lookup(search_term: str, conn: AsyncConnection) -> ExecutorResponse:
    searched_entity = resolve_entity(search_term, ["fuzzy"])
    query = jinja2.Template("""
    SELECT JSON_BUILD_OBJECT(
        'type', 'FeatureCollection',
        'features', JSON_AGG(
            JSON_BUILD_OBJECT(
                'type', 'Feature',
                'id', osm.id,
                'geometry', ST_AsGeoJSON(geom)::JSON,
                'properties', JSONB_BUILD_OBJECT(
                    'tags', tags
                )
            )
        )
    ) AS feature_collection
    FROM
      osm
    JOIN (
            {% if needle.match_type == "named_place" %}
                SELECT UNNEST('{ {{ needle.geoids | join(',') }} }'::VARCHAR[]) AS id
            {% elif needle.match_type == "category" %}
                SELECT osm_id AS id
                FROM category_membership
                WHERE 1=1
                    -- TODO how should we really do this?
                  AND human_readable ILIKE '%{{ needle.lookup }}%'
                LIMIT 100000
            {% else %}
                {# Otherwise, use the raw text lookup #}
                SELECT id
                FROM
                    osm,
                    plainto_tsquery( '{{ needle.lookup }}' ) query
                WHERE 1=1
                    AND query @@ fts
                LIMIT 100000
            {% endif %}
    ) queried ON queried.id = osm.id
    """).render(needle=searched_entity)
    geojson = (await conn.execute(text(query))).scalar()
    if geojson is None:
        raise ValueError("No results found")
    return ExecutorResponse(
        geom=geojson,
        entities=[ParsedEntity(**searched_entity.__dict__)],
    )


async def category_lookup(categories: List[str], conn: AsyncConnection) -> ExecutorResponse:
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
        SELECT DISTINCT osm_id AS id
        FROM category_membership
        WHERE category IN (:categories)
    ) queried ON queried.id = osm.id
    """).render(categories=categories)
    geojson = (await conn.execute(text(query))).scalar()
    if geojson is None:
        raise ValueError("No results found")
    return ExecutorResponse(
        geom=geojson,  # type: ignore
        entities=[],
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
    needle = resolve_entity(needle_place_or_amenity, enabled=["known_category", "fuzzy"])
    haystack = resolve_entity(haystack_place_or_amenity, enabled=["named_place"])  # Make sure it's a named place
    res = await conn.execute(text(jinja2.Template("""
        SELECT JSONB_BUILD_OBJECT(
            'type', 'FeatureCollection',
            'features', jsonb_agg(feature)
        )
        FROM (
          SELECT JSONB_BUILD_OBJECT(
              'type', 'Feature',
              'id', osm.id,
              'geometry', ST_AsGeoJSON(osm.geom)::JSONB,
              'properties', JSONB_BUILD_OBJECT(
                  'id', osm.id,
                  'tags', osm.tags
              )
          ) AS feature
          FROM
              osm
          JOIN (
                  {% if needle.match_type == "named_place" %}
                      SELECT UNNEST('{ {{ needle.geoids | join(',') }} }'::VARCHAR[]) AS id
                  {% elif needle.match_type == "category" %}
                      SELECT osm_id AS id
                      FROM category_membership
                      WHERE 1=1
                          -- TODO how should we really do this?
                        AND human_readable ILIKE '%{{ needle.lookup }}%'
                      LIMIT 100000
                  {% else %}
                      {# Otherwise, use the raw text lookup #}
                      SELECT id
                      FROM
                          osm,
                          plainto_tsquery( '{{ needle.lookup }}' ) query
                      WHERE 1=1
                          AND query @@ fts
                      LIMIT 100000
                  {% endif %}
          ) queried ON queried.id = osm.id
          WHERE 1=1
              AND ST_Intersects(geom,
               (
                  SELECT geom AS container_geom
                  FROM
                    osm
                  WHERE 1=1
                    AND (tags ? 'place' OR tags ? 'boundary')
                    AND id IN (
                        {{ geoids }}
                    )
                  GROUP BY 1
                  ORDER BY ST_Area(geom) DESC
                  LIMIT 1
               ))
        ) AS features
    """).render({"needle": needle, "haystack": haystack, "geoids": _prep_geoids(haystack.geoids)})))
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
    named_place_or_amenity_1: str | NamedPlaceParsedEntity,
    named_place_or_amenity_2: str | NamedPlaceParsedEntity,
    conn: AsyncConnection
) -> ExecutorResponse:
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
    anterior_locale = named_place(named_place_or_amenity_1 if isinstance(named_place_or_amenity_1, str) else named_place_or_amenity_1.lookup)
    posterior_locale = named_place(named_place_or_amenity_2 if isinstance(named_place_or_amenity_2, str) else named_place_or_amenity_2.lookup)
    if anterior_locale.pt is None or posterior_locale.pt is None:
        raise ValueError("anterior_locale or posterior_locale is None")
    routes = route(anterior_locale.pt.lng, anterior_locale.pt.lat, posterior_locale.pt.lng, posterior_locale.pt.lat, num_routes=3)
    print({
        "routes": routes
    })

    if not routes:
        raise ValueError("No routes found")

    templ = jinja2.Template("""
    WITH decoded_routes AS (
        {% for path in paths %}
        SELECT ST_Buffer(ST_LineFromEncodedPolyline('{{ path['points'] }}')::GEOGRAPHY, 200)::GEOMETRY AS geom
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
    {% if interior.match_type == 'category' %}
    JOIN osm_categories ON osm_categories.osm_id = osm.osm_id AND osm_categories.category = '{{ interior.lookup }}'
    {% elif interior.match_type == 'fuzzy' %}
    JOIN (
        SELECT id
        FROM
            osm,
            plainto_tsquery( '{{ interior.lookup }}' ) query
        WHERE 1=1
            AND query @@ fts
        LIMIT 100000
    ) AS fuzzy_matches ON fuzzy_matches.id = osm.id
    {% endif %}
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
        , NULL AS tags
        FROM decoded_routes
      ) AS subfeatures
    ) features;
    """).render(paths=routes.get('paths', []), interior=named_place_or_amenity_0)
    res = await conn.execute(text(templ))
    geom = res.scalar()
    return ExecutorResponse(
        geom=geom,  # type: ignore
        entities=[ParsedEntity(**named_place_or_amenity_0.__dict__), ParsedEntity(**named_place_or_amenity_1.__dict__), ParsedEntity(**named_place_or_amenity_2.__dict__)],
    )
