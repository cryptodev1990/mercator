import numpy as np

from app.data.presets import Preset
from app.parsers.categories import category_lookup
from typing import Optional
import jinja2
from app.core.datatypes import Point
from app.core.graphhopper import get_graph_hopper
from app.schemas import EnrichedEntity

import logging

logger = logging.getLogger(__name__)

MAX_DISTANCE_FOR_SEARCH_KM = 5000


def euclidean(lat0, lng0, lat1, lng1) -> float:
    """Calculate the distance between two lat-lon points and return result in meters

    This is also Eucledian distance, not geodesic distance. But it's good enough for our purposes.

    Examples
    --------
    >>> distance(0, 0, 0, 1)
    111000.0
    >>> distance(-10, -10, 10, 10)
    3139554.1084682713  # Real distance is closer to 3137km
    """
    dist = np.sqrt((lat0 - lat1) ** 2 + (lng0 - lng1) ** 2) * 111000
    return dist


def named_place(hopeful_place: str, map_centroid: Optional[Point] = Point(
    coordinates=[-98.5795, 39.8283],  # Center of the US
    type="Point",
), distance_cap_km=MAX_DISTANCE_FOR_SEARCH_KM) -> EnrichedEntity:
    """Look up named place in Nominatim via GraphHopper

    This is meant to be a rough first guess. We make sure the results is within some distance of the current map centroid.

    Returns a SQL snippet to be used in a WHERE clause.
    """
    gh = get_graph_hopper()
    response = gh.geocode(hopeful_place, limit=1)
    print(response)
    if not response:
        raise Exception("No results from GraphHopper")
    real_place = response["hits"][0]
    # Get the OSM ID
    osm_id = real_place["osm_id"]
    pt = real_place["point"]
    where = jinja2.Template("""
      AND osm_id = {{ osm_id }}
    """).render(osm_id=osm_id)
    if map_centroid and euclidean(pt['lat'], pt['lng'], map_centroid.coordinates[1], map_centroid.coordinates[0]) > distance_cap_km * 1000:
        logger.info({
            "message": "Named place is too far from map centroid",
            "place": hopeful_place,
            "distance": euclidean(pt['lat'], pt['lng'], map_centroid.coordinates[1], map_centroid.coordinates[0]),
        })
        raise Exception("Named place is too far from map centroid")
    return EnrichedEntity(
        lookup=hopeful_place,
        match_type="named_place",
        matched_geo_ids=[osm_id],
        sql_snippet=where,
    )


class NoCategoryMatchError(Exception):
    pass

from app.core.jinja_utils import squote

def known_category(hopeful_category: str) -> EnrichedEntity:
    """Match a known category to its relevant OSM lookup.
    """
    categories = category_lookup(hopeful_category)
    print(categories)
    if not categories:
        raise NoCategoryMatchError("No categories found")
    tmpl = jinja2.Template("""
            SELECT DISTINCT osm_id
            FROM category_membership
            WHERE category IN ({{ categories | join(", ") }})
    """)
    sql_snippet = tmpl.render(categories=[squote(p.key) for p in categories])
    return EnrichedEntity(
        lookup=hopeful_category,
        match_type="known_category",
        matched_geo_ids=[],
        sql_snippet=sql_snippet,
    )


def raw_lookup(hopeful_entity: str) -> EnrichedEntity:
    """Return the raw lookup as a SQL snippet.

    This is meant to be a rough first guess. We make sure the results is within some distance of the current map centroid.

    Returns a SQL snippet to be used in a WHERE clause.
    """
    # TODO is there a SQL injection-safe way to do this?
    sql_snippet = jinja2.Template("""
    SELECT osm_id
    FROM
      osm,
      WEBSEARCH_TO_TSQUERY('{{search_term}}') query,
      SIMILARITY('{{search_term}}', tags_text) similarity
    WHERE 1=1
      AND query @@ fts
      AND similarity > 0.01
    ORDER BY
      TS_RANK_CD(fts, query) DESC,
      similarity DESC
    LIMIT 100000
    """).render(search_term=hopeful_entity)
    return EnrichedEntity(
        lookup=hopeful_entity,
        match_type="raw_lookup",
        matched_geo_ids=[],
        sql_snippet=sql_snippet,
    )


def resolve_entity(hopeful_entity: str, enabled=set(["named_place", "known_category", "raw_lookup"])) -> EnrichedEntity:
    """Resolve an entity to a SQL snippet

    First, we check if the input is a named entity or a known category. If not, we pass the result through.

    Returns a SQL snippet to be used in a WHERE clause.
    """
    if "named_place" in enabled:
        try:
            print({
                "message": "Trying to resolve entity as a named place",
                "entity": hopeful_entity,
            })
            return named_place(hopeful_entity)
        except Exception as e:
            print("Failed with exception", e)
    if "known_category" in enabled:
        try:
            print({
                "message": "Trying to resolve entity as a known category",
                "entity": hopeful_entity,
            })
            return known_category(hopeful_entity)
        except Exception as e:
            print("Failed with exception", e)
    print({
        "message": "Could not resolve entity",
        "entity": hopeful_entity,
    })
    if "raw_lookup" in enabled:
        return raw_lookup(hopeful_entity)
    raise Exception(f"Entity {hopeful_entity} could not be resolved as a " + ", ".join(enabled))