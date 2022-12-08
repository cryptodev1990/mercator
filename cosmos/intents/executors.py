from sqlalchemy import text
from app.db import engine


def area_near_constraint(
    named_place_or_amenity_0: str,
    distance_or_time_0: str,
    named_place_or_amenity_1: str,
    distance_or_time_1: str,
    **kwargs
):
    print(f"Saw {named_place_or_amenity_0} {distance_or_time_0} {named_place_or_amenity_1} {distance_or_time_1}")


async def raw_lookup(search_term: str):
    async with engine.begin() as conn:  # type: ignore
        res = await conn.execute(text("""
        # build a geosjon feature collection
        SELECT JSONB_BUILD_OBJECT(
            'type', 'FeatureCollection',
            'features', jsonb_agg(feature)
        )
        FROM (
          SELECT JSONB_BUILD_OBJECT(
              'type', 'Feature',
              'id', osm_id,
              'geometry', ST_AsGeoJSON(osm_geom)::JSONB,
              'properties', JSONB_BUILD_OBJECT(
                  'osm_id', osm_id,   
                  'tags', tags
              )
          ) AS feature
          FROM 
              osm, 
              WEBSEARCH_TO_TSQUERY(:search_term) query,
              SIMILARITY(search_term, tags_text) similarity
          WHERE  1=1 
              AND query @@ fts
              AND similarity > 0.1
          ORDER BY 
              TS_RANK_CD(fts, query) DESC,
              similarity DESC
          LIMIT 100000;
      ) AS features
    """), dict(search_term=search_term))
    res = res.fetchall()
    return res


def x_within_time_or_distance_of_y(
    named_place_or_amenity_0: str,
    distance_or_time_0: str,
    named_place_or_amenity_1: str,
    distance_or_time_1: str,
):
    print(f"Saw {named_place_or_amenity_0} {distance_or_time_0} {named_place_or_amenity_1} {distance_or_time_1}")


def x_preposition_y(
    named_place_or_amenity_0: str,
    # prepositions can be 'in', 'near', 'at', 'around', 'within'
    preposition: str,
    named_place_or_amenity_1: str,
):
    print(f"Saw {named_place_or_amenity_0} {preposition} {named_place_or_amenity_1}")



def x_in_y(
    named_place_or_amenity_0: str,
    named_place_or_amenity_1: str,
):
    print(f"Saw {named_place_or_amenity_0} in {named_place_or_amenity_1}")

def x_near_y(
    named_place_or_amenity_0: str,
    named_place_or_amenity_1: str,
):
    print(f"Saw {named_place_or_amenity_0} near {named_place_or_amenity_1}")

def x_visible_from_y(
    named_place_or_amenity_0: str,
    named_place_or_amenity_1: str,
):
    print(f"Saw {named_place_or_amenity_0} visible from {named_place_or_amenity_1}")


def x_between_y(
    named_place_or_amenity_0: str,
    named_place_or_amenity_1: str,
    named_place_or_amenity_2: str,
):
    print(f"Saw {named_place_or_amenity_0} between {named_place_or_amenity_1} and {named_place_or_amenity_2}")

def x_on_y(
    named_place_or_amenity_0: str,
    named_place_or_amenity_1: str,
):
    print(f"Saw {named_place_or_amenity_0} on {named_place_or_amenity_1}")

def cluster(
    named_place_or_amenity_0: str,
):
    print(f"Saw {named_place_or_amenity_0}")

