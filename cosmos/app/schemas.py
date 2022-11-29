"""FastAPI response schemes."""
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

from app.core.datatypes import FeatureCollection
from app.parsers.rules import ParsedQuery


class Schema(BaseModel):
    """Base schema class."""


class HealthStatus(str, Enum):
    """Helath status codes."""

    OK = "OK"
    ERROR = "ERROR"


class HealthResponse(BaseModel):
    """Health response model."""

    message: HealthStatus


OsmQueryParse = ParsedQuery
"""Represents information about the parsed query.

The format of this dictionary is subject to change.
"""


class OsmSearchResponse(BaseModel):
    """Response for OSM search."""

    query: str = Field(..., description="The query string from the request.")
    label: Optional[str] = Field(
        None, description="A label that can be used to identify the query."
    )
    parse: Optional[OsmQueryParse] = Field(
        None,
        description=(
            "Details about how the query was parsed."
            "The format of this field is subject to change."
        ),
    )
    results: FeatureCollection = Field(
        ..., description="Feature collection of spatial features matching the query."
    )


class OsmRawQueryResponse(BaseModel):
    """Response for raw SQL executed against OSM."""

    query: str
    results: List[Dict[str, Any]]

    class Config:
        """Pydantic config options."""

        # pylint: disable=line-too-long
        schema_extra = {
            "example": {
                "query": "Oakland",
                "label": "Oakland",
                "parse": {
                    "value": {"type": "named_place", "value": ["Oakland"]},
                    "text": "Oakland",
                    "tokens": ["Oakland"],
                },
                "results": {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "id": "150980683",
                            "properties": {
                                "osm": {
                                    "id": 150980683,
                                    "tags": {
                                        "ele": "13",
                                        "name": "Oakland",
                                        "place": "city",
                                        "name:af": "Oakland",
                                        "name:an": "Oakland",
                                        "name:ar": "أوكلاند (كاليفورنيا)",
                                        "name:az": "Oklend",
                                        "name:be": "Окленд",
                                        "name:bg": "Оукланд",
                                        "name:bm": "Oakland",
                                        "name:bn": "ওকল্যান্ড",
                                        "name:br": "Oakland",
                                        "name:ca": "Oakland",
                                        "name:cs": "Oakland",
                                        "name:cy": "Oakland",
                                        "name:da": "Oakland",
                                        "name:de": "Oakland",
                                        "name:el": "Όουκλαντ",
                                        "name:en": "Oakland",
                                        "name:eo": "Oakland",
                                        "name:es": "Oakland",
                                        "name:et": "Oakland",
                                        "name:eu": "Oakland",
                                        "name:fa": "اوکلند، کالیفرنیا",
                                        "name:fi": "Oakland",
                                        "name:fr": "Oakland",
                                        "name:fy": "Oakland",
                                        "name:ga": "Oakland",
                                        "name:gl": "Oakland",
                                        "name:he": "אוקלנד (קליפורניה)",
                                        "name:hr": "Oakland",
                                        "name:ht": "Oakland",
                                        "name:hu": "Oakland",
                                        "name:hy": "Օքլենդ",
                                        "name:ia": "Oakland",
                                        "name:id": "Oakland",
                                        "name:ie": "Oakland",
                                        "name:io": "Oakland",
                                        "name:is": "Oakland",
                                        "name:it": "Oakland",
                                        "name:ja": "オークランド",
                                        "name:jv": "Oakland",
                                        "name:ka": "ოკლენდი",
                                        "name:ko": "오클랜드",
                                        "name:kw": "Oakland",
                                        "name:la": "Quercupolis",
                                        "name:li": "Oakland",
                                        "name:lt": "Oklandas",
                                        "name:lv": "Oklenda",
                                        "name:mg": "Oakland",
                                        "name:mk": "Оукленд",
                                        "name:ml": "ഓക്‌ലാന്റ്, കാലിഫോർണിയ",
                                        "name:mr": "ओकलंड",
                                        "name:ms": "Oakland",
                                        "name:ne": "ओकल्याण्ड",
                                        "name:nl": "Oakland",
                                        "name:nn": "Oakland i California",
                                        "name:no": "Oakland",
                                        "name:nv": "Chéchʼiltah Hatsoh",
                                        "name:oc": "Oakland",
                                        "name:pl": "Oakland",
                                        "name:pt": "Oakland",
                                        "name:ro": "Oakland",
                                        "name:ru": "Окленд",
                                        "name:sh": "Oakland",
                                        "name:sk": "Oakland",
                                        "name:sl": "Oakland",
                                        "name:so": "Oakland",
                                        "name:sq": "Oakland",
                                        "name:sr": "Оукланд",
                                        "name:sv": "Oakland",
                                        "name:sw": "Oakland",
                                        "name:ta": "ஓக்லண்ட், கலிபோர்னியா",
                                        "name:tl": "Oakland",
                                        "name:tr": "Oakland",
                                        "name:tt": "Оукленд",
                                        "name:uk": "Окленд",
                                        "name:ur": "اوکلینڈ، کیلیفورنیا",
                                        "name:uz": "Oakland",
                                        "name:vi": "Oakland",
                                        "name:vo": "Oakland",
                                        "name:yi": "אקלאנד, קאליפארניע",
                                        "name:yo": "Oakland",
                                        "name:zh": "奥克兰/奧克蘭/屋崙",
                                        "name:ast": "Oakland",
                                        "name:azb": "اوکلند",
                                        "name:ceb": "Oakland",
                                        "name:eml": "Oakland",
                                        "name:lmo": "Oakland",
                                        "name:mrj": "Окленд",
                                        "name:nan": "Oakland",
                                        "name:new": "ओकल्यान्ड, क्यालिफोर्निया",
                                        "name:pam": "Oakland",
                                        "name:pms": "Oakland",
                                        "name:pnb": "اوکلینڈ",
                                        "name:sco": "Oakland",
                                        "name:szl": "Oakland",
                                        "name:war": "Oakland",
                                        "name:yue": "奧克蘭",
                                        "wikidata": "Q17042",
                                        "wikipedia": "en:Oakland, California",
                                        "population": "433031",
                                        "name:zh-Hans": "奥克兰",
                                        "name:zh-Hant": "奧克蘭",
                                        "name:be-tarask": "Оўклэнд",
                                        "name:zh-Hant-HK": "屋崙",
                                        "name:zh-Hant-TW": "奧克蘭",
                                        "population:date": "2019",
                                        "census:population": "433031;2019",
                                    },
                                    "type": "N",
                                    "category": "point",
                                }
                            },
                            "geometry": {"type": "Point", "coordinates": [-122.271356, 37.8044557]},
                            "bbox": [-122.271356, 37.8044557, -122.271356, 37.8044557],
                        }
                    ],
                    "bbox": [-122.271356, 37.8044557, -122.271356, 37.8044557],
                },
            }
        }

    # pylint: enable=line-too-long
