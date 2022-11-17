"""Functions to parse search queries."""
import logging
import re
from typing import Any, Callable, Dict, List, Match, Optional, Type, Union

from fastapi import HTTPException
from geoalchemy2 import Geography
from sqlalchemy import func
from sqlalchemy.sql import ColumnElement, case, cast

logger = logging.getLogger(__name__)

START_PAT = "(?i:what|which|find all|find the|find which|show me|show all|show the|show which|list all|list the|list which|list|show|find)"  # pylint: disable=line-too-long

NEAR_METERS = 1000


class SpatialRelation:
    """Generate SQL for a spatial relation between two geometries."""

    def __init__(
        self, **kwargs: Dict[str, Any]  # pylint: disable=unused-argument
    ) -> None:
        ...

    def __call__(self, geom_a: ColumnElement, geom_b: ColumnElement) -> ColumnElement:
        raise NotImplementedError


class InSpRelation(SpatialRelation):
    """Generate SQL for A in B spatial relation."""

    def __call__(self, geom_a: ColumnElement, geom_b: ColumnElement) -> ColumnElement:
        return func.St_CoveredBy(geom_a, geom_b)


class BordersSpRelation(SpatialRelation):
    """Generate SQL for A borders B spatial relation."""

    def __call__(self, geom_a: ColumnElement, geom_b: ColumnElement) -> ColumnElement:
        return func.St_Intersects(geom_a, geom_b)


class CrossesSpRelation(SpatialRelation):
    """Generate SQL for A crosses B spatial relation."""

    def __call__(self, geom_a: ColumnElement, geom_b: ColumnElement) -> ColumnElement:
        return func.St_Intersects(geom_a, geom_b)


class AtMostDistSpRelation(SpatialRelation):
    """Generate SQL for A is at most x units from B spatial relation."""

    def __init__(self, dist: int) -> None:
        super().__init__()
        self.dist = dist

    def __call__(self, geom_a: ColumnElement, geom_b: ColumnElement) -> ColumnElement:
        return func.St_DWithin(
            cast(geom_a, Geography), cast(geom_b, Geography), self.dist
        )


class AtLeastDistSpRelation(SpatialRelation):
    """Generate SQL for A is at least x units from B spatial relation."""

    def __init__(self, dist: int) -> None:
        super().__init__()
        self.dist = dist

    def __call__(self, geom_a: ColumnElement, geom_b: ColumnElement) -> ColumnElement:
        return func.St_Distance(geom_a, geom_b) > self.dist


def _sql_direction(geom_a: ColumnElement, geom_b: ColumnElement) -> ColumnElement:
    degrees = func.degrees(func.ST_Azimuth(geom_b, geom_a)) % 360
    expr = case(
        (degrees < 45, "N"),
        (degrees < 135, "E"),
        (degrees < 225, "S"),
        (degrees < 315, "W"),  # type: ignore
        else_="N",
    )
    return expr


class DirectionSpRelation(SpatialRelation):
    """Generate SQL for A is (north|south|east|west) of B."""

    def __init__(self, direction: str) -> None:
        super().__init__()
        self.direction = direction

    def __call__(self, geom_a: ColumnElement, geom_b: ColumnElement) -> ColumnElement:
        return _sql_direction(geom_a, geom_b) == self.direction


class _RelationPattern:
    def __init__(
        self,
        relation: Type[SpatialRelation],
        patterns: Union[List[str], str],
        process_match: Optional[Callable[[Match[str]], Dict[str, Any]]] = None,
    ) -> None:
        self.patterns: List[str]
        if isinstance(patterns, str):
            self.patterns = [patterns]
        else:
            self.patterns = [str(pat) for pat in patterns]
        self.relation = relation
        self.process_match = process_match

    def __call__(self, text: str) -> Optional[Dict[str, Any]]:
        for pat in self.patterns:
            full_pattern = (
                "^(?P<figure>.*)\\s+(?P<relation>(?i:"
                + pat
                + "))\\s+(?P<ground>.*?)[.?!,;]?$"
            )
            m = re.search(full_pattern, text)
            if m:
                if callable(self.process_match):
                    kwargs = self.process_match(m)
                else:
                    kwargs = {}
                relation = self.relation(**kwargs)
                return {
                    "figure": m.group("figure"),
                    "ground": m.group("ground"),
                    "relation": relation,
                    "relation_text": m.group("relation"),
                }
        return None


def _process_dist_match(m: Match[str]) -> Dict[str, Any]:
    dist = m.group("dist")
    if dist is None:
        raise ValueError("Dist group not found")
    num_dist = float(dist)
    units = m.group("units")
    if units is None:
        raise ValueError("Units group not found")
    if units in ["km", "kilometers"]:
        value = num_dist * 1000
    elif units in ["miles", "mile", "mi"]:
        value = num_dist * 1609.34
    else:
        raise ValueError(f"Unit = {units} not supported")
    return {"dist": value}


_RELATION_PATTERNS = {
    # Topology
    "in": _RelationPattern(
        InSpRelation, ["(?:in|inside|is located in|is included in|within)"]
    ),
    "crosses": _RelationPattern(
        CrossesSpRelation, ["(?:cross|intersect|crosses|intersects)"]
    ),
    "borders": _RelationPattern(
        BordersSpRelation,
        [
            "that borders",
            "bordering",
            "(?:is|are) at the border of",
            "(?:is|are) at the outskirts of",
            "(?:is|are) at the boundary of",
        ],
    ),
    # distances
    "near": _RelationPattern(
        AtMostDistSpRelation,
        r"(?:near|nearby|close to|around)",
        lambda m: {"dist": NEAR_METERS},
    ),
    "at most x units": _RelationPattern(
        AtMostDistSpRelation,
        r"at most (?P<dist>\d+) (?P<unit>kilometers?|km|miles?|mi)\.?",
        process_match=_process_dist_match,
    ),
    "at least x units": _RelationPattern(
        AtLeastDistSpRelation,
        r"at least (?P<dist>\d+) (?P<unit>kilometers?|km|miles|mi)\.?",
        process_match=_process_dist_match,
    ),
    "north": _RelationPattern(
        DirectionSpRelation, r"(?:to the )?north(?: of)?", lambda m: {"direction": "N"}
    ),
    "south": _RelationPattern(
        DirectionSpRelation, r"(?:to the )?south(?: of)?", lambda m: {"direction": "S"}
    ),
    "east": _RelationPattern(
        DirectionSpRelation, r"(?:to the )?east(?: of)?", lambda m: {"direction": "E"}
    ),
    "west": _RelationPattern(
        DirectionSpRelation, r"(?:to the )?west(?: of)?", lambda m: {"direction": "W"}
    ),
}


def parse_query(query: str) -> Dict[str, Any]:
    """Parse an OSM query."""

    for _, pattern in _RELATION_PATTERNS.items():
        if relation := pattern(query):
            return relation
    raise HTTPException(status_code=400, detail="Query not understood")
