"""Parser for distance strings."""
import re
from typing import List

from pint import Quantity, UnitRegistry

ureg = UnitRegistry()

_units = {
    "km": (r"km?|kilometers?|kilometres?", ureg.kilometer),
    "m": (r"m|meters?|metres?", ureg.meter),
    "mi": (r"mi|miles?", ureg.mile),
    # yeah - no one is going to use nautical miles but it appears in OSM
    # https://wiki.openstreetmap.org/wiki/Map_features/Units
    "nmi": (r"nmi|(?:international\s*)?nautical\s*miles?", ureg.nautical_mile),
    "yd": (r"yd|yard|yards", ureg.yard),
    "ft": (r"ft|feet|'|′", ureg.foot),
    "in": (r"in|inch|inches|\"|″", ureg.inch),
}
DIST_PATTERNS = [
    (
        re.compile(r"(\d+(?:\.\d+)?|\.\d+)\s*(?:" + pattern + r")(?=[^A-Za-z]|$)", re.IGNORECASE),
        unit,
    )
    for pattern, unit in _units.values()
]
del _units


def parse(string: str) -> List[Quantity]:
    """Parse a distance string and return the number of meters.

    The patterns here assume that the provided string has already been
    classified as a distance string. This should not be used to determine
    whether a string is a distance string.

    This function currently only supports units relevant to the queries in this app.

    - kilometers: "km", "kilometer", "kilometers", "kilometre", "kilometres"
    - meters: "m", "meter", "meters", "metre", "metres"
    - miles: "mi", "mile", "miles"

    Args:
        string (str): Distance string to parse.
    Returns:
        List[Quantity]: List of distance quantities.

    """
    dist: List[Quantity] = []
    for pattern, unit in DIST_PATTERNS:
        if match := pattern.search(string):
            qnty = Quantity(float(match.group(1)), unit)
            if dist is None:
                dist.append(qnty)
            else:
                dist.append(qnty)
    if not dist:
        raise ValueError(f"Could not parse string: {string}")
    return dist
