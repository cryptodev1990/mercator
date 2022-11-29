from datetime import timedelta
from typing import List, Tuple

import pytest
from pint import Quantity

from app.parsers.rules import (
    Buffer,
    Isochrone,
    NamedPlace,
    Place,
    QueryIntents,
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
]


@pytest.mark.parametrize("example,expected", examples)
def test_parse_works(example: str, expected: QueryIntents) -> None:
    assert parse(example).value == expected
