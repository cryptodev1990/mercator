from datetime import timedelta
from typing import Union

import pytest

from app.parsers.time import parse, readable_duration

examples = [
    ("0 minutes", 0),
    ("10 minutes", 600),
    ("10 min", 600),
    ("0 m", 0),
    ("10.5min", 630),
    ("10 minutes and 30 seconds", 630),
    ("10 minutes 30 seconds", 630),
    ("1 hour 10 minute 30 second", 4230),
    ("23 hours and 1 minutes and 30 seconds", 82890),
    ("1h10m30s", 4230),
    ("1:02", 3720),
    ("10:09:08", 36548),
]


@pytest.mark.parametrize("string,expected", examples)
def test_parse(string: str, expected: float) -> None:
    """Test that parse() returns the expected value."""
    assert parse(string) == timedelta(seconds=expected)


def test_bad_input() -> None:
    """Test that parse() raises an exception on bad input."""
    with pytest.raises(ValueError):
        parse("bad input")


@pytest.mark.parametrize(
    "time,expected",
    [
        (0, "0 minutes"),
        (1, "1 second"),
        (2, "2 seconds"),
        (60, "1 minute"),
        (61, "1 minute 1 second"),
        (62, "1 minute 2 seconds"),
        (120, "2 minutes"),
        (3600, "1 hour"),
        (3601, "1 hour 1 second"),
        (3723, "1 hour 2 minutes 3 seconds"),
        (timedelta(seconds=120), "2 minutes"),
    ],
)
def test_readable_duration(time: Union[timedelta, float], expected: str) -> None:
    """Test that parse() returns the expected value."""
    assert readable_duration(time) == expected


def test_readable_duration_negative_number() -> None:
    """Test that readable_duration() raises an exception with negative numbers."""
    with pytest.raises(ValueError):
        readable_duration(-1)


def test_readable_duration_unsupported_type() -> None:
    """Test that readable_duration() raises an exception with negative numbers."""
    with pytest.raises(NotImplementedError):
        readable_duration("foo")
