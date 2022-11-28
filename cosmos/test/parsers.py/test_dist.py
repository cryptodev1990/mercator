"""Tests for app.parsers.dist module."""
from typing import List

import pytest
from pint import Quantity, UnitRegistry

from app.parsers.dist import parse

ureg = UnitRegistry()

examples = [
    ("1.5 meter", [Quantity(1.5, "meter")]),
    (".2 metre", [Quantity(0.2, "meter")]),
    ("3 metres", [Quantity(3, "meter")]),
    ("10 m", [Quantity(10, "meter")]),
    ("123 m. other stuff", [Quantity(123, "meter")]),
    ("1 km", [Quantity(1, "kilometer")]),
    ("2 kilometer", [Quantity(2, "kilometer")]),
    ("3 kilometers", [Quantity(3, "kilometer")]),
    ("4 kilometre", [Quantity(4, "kilometer")]),
    ("11 kilometres", [Quantity(11, "kilometer")]),
    ("1 mi.", [Quantity(1, "mile")]),
    ("1 mile", [Quantity(1, "mile")]),
    ("2 miles", [Quantity(2, "mile")]),
    ("1 nmi", [Quantity(1, "nautical_mile")]),
    ("1 nautical mile", [Quantity(1, "nautical_mile")]),
    ("1 kilometer 2 m", [Quantity(1, "kilometer"), Quantity(2, "meter")]),
    ("100 feet", [Quantity(100, "foot")]),
    ("100 ft 1in", [Quantity(100, "foot"), Quantity(1, "inch")]),
    ("100'", [Quantity(100, "foot")]),
    ("100 inch", [Quantity(100, "inch")]),
    ("100 in", [Quantity(100, "inch")]),
    ('100"', [Quantity(100, "inch")]),
]


@pytest.mark.parametrize("string,expected", examples)
def test_parse(string: str, expected: List[Quantity]) -> None:
    """Test that parse() returns the expected value."""
    assert set(parse(string)) == set(expected)


def test_bad_input() -> None:
    """Test that parse() raises an exception on bad input."""
    with pytest.raises(ValueError):
        parse("bad input")
