from datetime import timedelta
from typing import Any, List, Tuple

import pytest
from pint import Quantity

from app.parsers.rules import (
    Buffer,
    Isochrone,
    NamedPlace,
    Place,
    QueryIntents,
    QueryParseError,
    Route,
    SpRelCoveredBy,
    SpRelDisjoint,
    SpRelNear,
    SpRelNotNear,
    SpRelOutsideDistOf,
    SpRelOutsideTimeOf,
    SpRelWithinDistOf,
    SpRelWithinTimeOf,
    parse,
)

examples: List[Tuple[str, QueryIntents]] = [
    ("Shops", Place(value=["Shops"])),
    ("San Francisco", NamedPlace(value=["San Francisco"])),
    ("Chinese restaurants", Place(value=["Chinese", "restaurants"])),
    (
        "San Francisco shops",
        SpRelCoveredBy(object=NamedPlace(value=["San Francisco"]), subject=Place(value=["shops"])),
    ),
    (
        "Shops in San Francisco",
        SpRelCoveredBy(object=NamedPlace(value=["San Francisco"]), subject=Place(value=["Shops"])),
    ),
    (
        "Shops not inside San Francisco",
        SpRelDisjoint(object=NamedPlace(value=["San Francisco"]), subject=Place(value=["Shops"])),
    ),
    (
        "Shops near San Francisco",
        SpRelNear(object=NamedPlace(value=["San Francisco"]), subject=Place(value=["Shops"])),
    ),
    (
        "Shops not near to San Francisco",
        SpRelNotNear(object=NamedPlace(value=["San Francisco"]), subject=Place(value=["Shops"])),
    ),
    (
        "Shops within 10 minutes of San Francisco",
        SpRelWithinTimeOf(
            object=NamedPlace(value=["San Francisco"]),
            subject=Place(value=["Shops"]),
            duration=timedelta(minutes=10),
        ),
    ),
    (
        "Shops not within 10 minutes of San Francisco",
        SpRelOutsideTimeOf(
            object=NamedPlace(value=["San Francisco"]),
            subject=Place(value=["Shops"]),
            duration=timedelta(minutes=10),
        ),
    ),
    (
        "Shops within 10 miles of San Francisco",
        SpRelWithinDistOf(
            object=NamedPlace(value=["San Francisco"]),
            subject=Place(value=["Shops"]),
            distance=Quantity(10, "miles").to("meters").magnitude,
        ),
    ),
    (
        "Shops not within 10 miles of San Francisco",
        SpRelOutsideDistOf(
            object=NamedPlace(value=["San Francisco"]),
            subject=Place(value=["Shops"]),
            distance=Quantity(10, "miles").to("meters").magnitude,
        ),
    ),
    (
        "Buffer of 10 miles around San Francisco",
        Buffer(
            object=NamedPlace(value=["San Francisco"]),
            distance=Quantity(10, "miles").to("meters").magnitude,
        ),
    ),
    (
        "Buffer of 10 minutes around San Francisco",
        Isochrone(object=NamedPlace(value=["San Francisco"]), duration=timedelta(minutes=10)),
    ),
    (
        "Route from Los Angeles to San Francisco",
        Route(start=NamedPlace(value=["Los Angeles"]), end=NamedPlace(value=["San Francisco"])),
    ),
    (
        "Shops along the route from Los Angeles to San Francisco",
        Route(
            start=NamedPlace(value=["Los Angeles"]),
            end=NamedPlace(value=["San Francisco"]),
            along=Place(value=["Shops"]),
        ),
    ),
    (
        "Get me all the shops that are near San Francisco",
        SpRelNear(
            object=NamedPlace(value=["San Francisco"]), subject=Place(value=["all", "the", "shops"])
        ),
    ),
    (
        "route San Francisco to Oakland",
        Route(start=NamedPlace(value=["San Francisco"]), end=NamedPlace(value=["Oakland"])),
    ),
    (
        "All the coffee shops in San Francisco",
        SpRelCoveredBy(
            subject=Place(value=["All", "the", "coffee", "shops"]),
            object=NamedPlace(value=["San Francisco"]),
        ),
    ),
    (
        "coffee shops in richmond",
        SpRelCoveredBy(
            subject=Place(value=["coffee", "shops"]), object=NamedPlace(value=["richmond"])
        ),
    ),
    (
        "All the coffee shops within 20m of Alamo Square",
        SpRelWithinDistOf(
            subject=Place(value=["All", "the", "coffee", "shops"]),
            object=Place(value=["Alamo Square"]),
            distance=20,
        ),
    ),
    (
        "All the coffee shops within 20 ft of Alamo Square",
        SpRelWithinDistOf(
            subject=Place(value=["All", "the", "coffee", "shops"]),
            object=Place(value=["Alamo Square"]),
            distance=6.096,
        ),
    ),
    (
        "All the coffee shops within 20 yd of Alamo Square",
        SpRelWithinDistOf(
            subject=Place(value=["All", "the", "coffee", "shops"]),
            object=Place(value=["Alamo Square"]),
            distance=18.288,
        ),
    ),
    (
        "Coastal campsites",
        Place(value=["Coastal", "campsites"]),
    ),
    (
        "All the coffee shops in California",
        SpRelCoveredBy(
            subject=Place(value=["All", "the", "coffee", "shops"]),
            object=NamedPlace(value=["California"]),
            distance=18.288,
        ),
    ),
    ("zip line", Place(value=["zip", "line"])),
    ("zipline", Place(value=["zipline"])),
    ("phone booth", Place(value=["phone", "booth"])),
    ("camping site", Place(value=["camping", "site"])),
    ("light pole", Place(value=["light", "pole"])),
    ("Coastal camping sites", Place(value=["Coastal", "camping", "sites"])),
]


def compare_outside_dist_of(a: SpRelOutsideDistOf, b: Any) -> bool:
    assert isinstance(a, SpRelOutsideDistOf) and isinstance(b, SpRelOutsideDistOf)
    return (
        a.object == b.object
        and a.subject == b.subject
        and a.distance == pytest.approx(b.distance, 0.01)
    )


def compare_within_dist_of(a: SpRelWithinDistOf, b: Any) -> bool:
    assert isinstance(a, SpRelWithinDistOf) and isinstance(b, SpRelWithinDistOf)
    return (
        a.object == b.object
        and a.subject == b.subject
        and a.distance == pytest.approx(b.distance, 0.01)
    )


@pytest.mark.parametrize("example,expected", examples)
def test_parse_works(example: str, expected: QueryIntents) -> None:
    actual = parse(example).value
    if isinstance(expected, SpRelOutsideDistOf):
        compare_outside_dist_of(expected, actual)
    elif isinstance(expected, SpRelWithinDistOf):
        compare_within_dist_of(expected, actual)
    else:
        assert actual == expected


def text_error_for_empty_query() -> None:
    with pytest.raises(QueryParseError):
        parse("")
