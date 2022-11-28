"""Parser for time strings."""
import re
from datetime import timedelta

NUMBER_PAT = r"(?P<value>\d+(?:\.\d+)?|\.\d+)"
NOT_FOLLOWED_BY_LETTER_PAT = r"(?=[^A-Za-z]|$)"

RE_MINUTE = NUMBER_PAT + r"\s*(?:m|mins?|minutes?)" + NOT_FOLLOWED_BY_LETTER_PAT
RE_SECOND = NUMBER_PAT + r"\s*(?:s|secs?|seconds?)" + NOT_FOLLOWED_BY_LETTER_PAT
RE_HOUR = NUMBER_PAT + r"\s*(?:h|hrs?|hours?)" + NOT_FOLLOWED_BY_LETTER_PAT
RE_HMS = r"(?P<h>\d+):(?P<m>\d+)(?::(?P<s>\d+))?"


def parse(string: str) -> timedelta:
    """Parse a time string and return the number of seconds.

    This function currently supports times relevant to durations in isochrones:

    - hours: "h", "hr", "hrs", "hour", "hours"
    - minutes: "m", "min", "mins", "minute", "minutes"
    - seconds: "s", "sec", "secs", "second", "seconds"

    Args:
        string (str): Time string to parse.
    Returns:
        timedelta: The duration specified by the string.
    """

    has_match = False
    hour = minute = second = 0.0
    if match_min := re.search(RE_MINUTE, string, re.I):
        minute = float(match_min.group("value"))
        has_match = True
    if match_sec := re.search(RE_SECOND, string, re.I):
        second = float(match_sec.group("value"))
        has_match = True
    if match_hour := re.search(RE_HOUR, string, re.I):
        hour = float(match_hour.group("value"))
        has_match = True

    if not has_match:
        if match_hms := re.search(RE_HMS, string, re.I):
            hour = float(match_hms.group("h"))
            minute = float(match_hms.group("m"))
            second = float(match_hms.group("s") or 0)
            has_match = True
    if not has_match:
        if match_any_num := re.search(NUMBER_PAT, string, re.I):
            minute = float(match_any_num.group("value"))
            has_match = True
    if not has_match:
        raise ValueError(f"Could not parse string: {string}")
    return timedelta(hours=hour, minutes=minute, seconds=second)
