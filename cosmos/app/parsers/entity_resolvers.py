import re

DIST_REGEX = r'^(?P<distance>\d+(?:\.\d+)?)\s?(?P<unit>meter|meters|m|km|mi|mile|miles|kilometer|kilometers|feet|foot|yard|yards)$'
TIME_REGEX = r'^(?P<time>\d+(?:\.\d+)?)\s?(?P<unit>s|sec|secs|seconds|second|min|mins|minutes|minute|hr|hrs|hours|hour)$'

def parse_into_meters(
    text: str, default_m=None
) -> float:
    """Function that takes a string, parses out a distance or a time"""
    text = text.strip()
    if text == '' and default_m is not None:
        return default_m
    matched = re.match(DIST_REGEX, text)
    if matched:
        return Distance(text).distance_in_meters
    raise ValueError(f'Could not parse {text} as a distance')


def parse_into_seconds(
    text: str,
) -> float:
    """Function that takes a string, parses out a distance or a time"""
    text = text.strip()
    matched = re.match(TIME_REGEX, text)
    if matched:
        return Time(text).time_in_seconds
    raise ValueError(f'Could not parse {text} as a time')

class Distance:
    def __init__(self, text: str):
        """Function that takes a string, parses out a distance or a time"""
        text = text.strip()
        matched = re.match(DIST_REGEX, text)
        if matched:
            self.distance = float(matched.group('distance'))
            self.unit = str(matched.group('unit'))
            self.distance_in_meters = self.convert_to_meters()
        else:
            raise ValueError(f'Could not parse {text} as a distance')
    
    def convert_to_meters(self):
        if self.unit in ('m', 'meter', 'meters'):
            return self.distance
        elif self.unit in ('km', 'kilometer', 'kilometers'):
            return self.distance * 1000
        elif self.unit in ('mi', 'mile', 'miles'):
            return self.distance * 1609.34
        elif self.unit in ('ft', 'feet', 'foot'):
            return self.distance * 0.3048
        elif self.unit in ('yd', 'yard', 'yards'):
            return self.distance * 0.9144
        else:
            raise ValueError(f'Unit {self.unit} not supported')

    def __str__(self):
        return f'{self.distance} {self.unit}'


class Time:
    def __init__(self, text: str):
        """Function that takes a string, parses out a distance or a time"""
        matched = re.match(TIME_REGEX, text)
        text = text.strip()
        if matched:
            self.time = float(matched.group('time'))
            self.unit = str(matched.group('unit'))
            self.time_in_seconds = self.convert_to_seconds()
        else:
            raise ValueError(f'Could not parse {text} as a time')
        
    def convert_to_seconds(self) -> float:
        if self.unit in ['s', 'sec', 'secs', 'seconds', 'second']:
            return self.time * 1.0
        elif self.unit in ['min', 'mins', 'minutes', 'minute']:
            return self.time * 60
        elif self.unit in ['hr', 'hrs', 'hours', 'hour']:
            return self.time * 3600
        else:
            raise ValueError(f'Unit {self.unit} not supported')

    def __str__(self):
        return f'{self.time} {self.unit}'