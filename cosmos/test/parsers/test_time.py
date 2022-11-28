from datetime import timedelta

import pytest

from app.parsers.time import parse

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
