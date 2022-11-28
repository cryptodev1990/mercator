"""FastAPI response schemes."""
from enum import Enum
from typing import Annotated, Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

from app.core.datatypes import BBox, FeatureCollection


class Schema(BaseModel):
    """Base schema class."""


class HealthStatus(str, Enum):
    """Helath status codes."""

    OK = "OK"
    ERROR = "ERROR"


class HealthResponse(BaseModel):
    """Health response model."""

    message: HealthStatus


class Place(BaseModel):
    """A place in a place query.

    The full place query also can include spatial relations.

    """

    text: Optional[str] = None
    is_named: bool = False
    bbox: Optional[BBox] = None


class SpRel(BaseModel):
    """A spatial relationship between geometries."""

    object: Place


class SpRelContains(SpRel):
    """The spatial relationship A is covered by B."""

    type: Literal["contains"] = "contains"


class SpRelCoveredBy(SpRel):
    """The spatial relationship A is covered by B."""

    type: Literal["covered_by"] = "covered_by"


class SpRelDisjoint(SpRel):
    """The spatial relationship A is covered by B."""

    type: Literal["disjoint"] = "disjoint"


SpatialRelation = Annotated[
    Union[SpRelContains, SpRelDisjoint, SpRelCoveredBy],
    Field(discriminator="type"),
]
"""Union of all spatial relations.

The discriminator field is used to determine the type of the spatial relation.
"""

OsmQueryParse = Dict[str, Any]
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

    class Config:
        """Pydantic config options."""

        schema_extra = {
            "example": [
                {
                    "query": "Coffee shops in San Francisco",
                    "label": "Coffee shops in San Francisco",
                    "parse": {
                        "intent": "covered_by",
                        "args": {
                            "subject": {"text": "Coffee shops", "start": 0, "end": 12},
                            "predicate": {"text": "in", "start": 13, "end": 15},
                            "object": {"text": "San Francisco", "start": 16, "end": 29},
                        },
                        "model": "regex-0.0.2",
                    },
                    "results": {
                        "type": "FeatureCollection",
                        "features": [
                            {
                                "type": "Feature",
                                "id": "331477411",
                                "properties": {
                                    "osm": {
                                        "id": 331477411,
                                        "tags": {
                                            "name": "Starbucks",
                                            "brand": "Starbucks",
                                            "amenity": "cafe",
                                            "cuisine": "coffee_shop",
                                            "building": "yes",
                                            "takeaway": "yes",
                                            "official_name": "Starbucks Coffee",
                                            "brand:wikidata": "Q37158",
                                            "brand:wikipedia": "en:Starbucks",
                                        },
                                        "type": "W",
                                        "category": "polygon",
                                    }
                                },
                                "geometry": {
                                    "type": "Polygon",
                                    "coordinates": [
                                        [
                                            [-121.8453238, 37.6985964],
                                            [-121.8453111, 37.6984312],
                                            [-121.8452404, 37.6984346],
                                            [-121.8452065, 37.6984668],
                                            [-121.8452133, 37.69854],
                                            [-121.8452025, 37.6985409],
                                            [-121.8452057, 37.6986019],
                                            [-121.8453238, 37.6985964],
                                        ]
                                    ],
                                },
                                "bbox": [-121.8453238, 37.6984312, -121.8452025, 37.6986019],
                            },
                            {
                                "type": "Feature",
                                "id": "5061128432",
                                "properties": {
                                    "osm": {
                                        "id": 5061128432,
                                        "tags": {
                                            "name": "Andytown Coffee Roasters",
                                            "amenity": "cafe",
                                            "cuisine": "coffee_shop",
                                            "addr:city": "San Francisco",
                                            "addr:state": "CA",
                                            "addr:street": "Taraval Street",
                                            "addr:postcode": "94116",
                                            "opening_hours": "Mo-Th 08:00-15:00; Fr-Su 08:00-17:00",
                                            "outdoor_seating": "yes",
                                            "addr:housenumber": "3629",
                                        },
                                        "type": "N",
                                        "category": "point",
                                    }
                                },
                                "geometry": {
                                    "type": "Point",
                                    "coordinates": [-122.5051837, 37.7416331],
                                },
                                "bbox": [-122.5051837, 37.7416331, -122.5051837, 37.7416331],
                            },
                        ],
                    },
                }
            ]
        }


class OsmRawQueryResponse(BaseModel):
    """Response for raw SQL executed against OSM."""

    query: str
    results: List[Dict[str, Any]]

    class Config:
        """Pydantic config options."""

        # pylint: disable=line-too-long
        schema_extra = {
            "example": {
                "query": "SELECT osm_type, osm_id, tags FROM osm WHERE tags->>'name' = 'San Francisco' and category = 'boundary' LIMIT 1",
                "results": [
                    {
                        "osm_type": "R",
                        "osm_id": 111968,
                        "attrs": {},
                        "tags": {
                            "name": "San Francisco",
                            "type": "boundary",
                            "place": "city",
                            "name:af": "San Francisco",
                            "name:am": "ሳን ፍራንሲስኰ",
                            "name:an": "San Francisco",
                            "name:ar": "سان فرانسيسكو",
                            "name:az": "San-Fransisko",
                            "name:ba": "Сан-Франциско",
                            "name:be": "Сан-Францыска",
                            "name:bg": "Сан Франциско",
                            "name:bm": "San Francisco",
                            "name:bn": "সান ফ্রান্সিস্কো",
                            "name:bo": "སན་ཧྥུ་རན་སིས་ཁོ",
                            "name:br": "San Francisco",
                            "name:bs": "San Francisco",
                            "name:ca": "San Francisco",
                            "name:ce": "Сан-Франциско",
                            "name:co": "San Francisco",
                            "name:cs": "San Francisco",
                            "name:cv": "Сан-Франциско",
                            "name:cy": "San Francisco",
                            "name:da": "San Francisco",
                            "name:de": "San Francisco",
                            "name:el": "Σαν Φρανσίσκο",
                            "name:en": "San Francisco",
                            "name:eo": "San-Francisko",
                            "name:es": "San Francisco",
                            "name:et": "San Francisco",
                            "name:eu": "San Frantzisko",
                            "name:fa": "سان فرانسیسکو",
                            "name:fi": "San Francisco",
                            "name:fj": "San Francisco",
                            "name:fo": "San Francisco",
                            "name:fr": "San Francisco",
                            "name:fy": "San Francisco",
                            "name:ga": "San Francisco",
                            "name:gd": "San Francisco",
                            "name:gl": "San Francisco",
                            "name:gv": "San Francisco",
                            "name:ha": "San Francisco",
                            "name:he": "סן פרנסיסקו",
                            "name:hi": "सैन फ़्रांसिस्को",
                            "name:hr": "San Francisco",
                            "name:ht": "San Francisco",
                            "name:hu": "San Francisco",
                            "name:hy": "Սան Ֆրանցիսկո",
                            "name:ia": "San Francisco",
                            "name:id": "San Francisco",
                            "name:ie": "San Francisco",
                            "name:io": "San Francisco",
                            "name:is": "San Francisco",
                            "name:it": "San Francisco",
                            "name:ja": "サンフランシスコ",
                            "name:jv": "San Francisco",
                            "name:ka": "სან-ფრანცისკო",
                            "name:ki": "San Francisco",
                            "name:kk": "Сан-Франциско",
                            "name:ko": "샌프란시스코",
                            "name:ku": "San Francisco",
                            "name:kw": "San Francisco",
                            "name:ky": "Сан-Франциско",
                            "name:la": "Franciscopolis",
                            "name:lb": "San Francisco",
                            "name:li": "San Francisco",
                            "name:ln": "San Francisco",
                            "name:lt": "San Fransiskas",
                            "name:lv": "Sanfrancisko",
                            "name:mg": "San Francisco",
                            "name:mi": "Hana Paraniko",
                            "name:mk": "Сан Франциско",
                            "name:ml": "സാൻ ഫ്രാൻസിസ്കോ",
                            "name:mn": "Сан-Франциско",
                            "name:mr": "सॅन फ्रान्सिस्को",
                            "name:ms": "San Francisco",
                            "name:my": "ဆန်ဖရန်စစ္စကိုမြို့",
                            "name:na": "San Francisco",
                            "name:ne": "सान फ्रान्सिस्को",
                            "name:nl": "San Francisco",
                            "name:nn": "San Francisco",
                            "name:no": "San Francisco",
                            "name:nv": "Naʼníʼá Hóneezí",
                            "name:oc": "San Francisco",
                            "name:os": "Сан-Франциско",
                            "name:pa": "ਸਾਨ ਫ਼ਰਾਂਸਿਸਕੋ",
                            "name:pl": "San Francisco",
                            "name:ps": "سان فرانسسکو",
                            "name:pt": "São Francisco",
                            "name:qu": "San Francisco",
                            "name:ro": "San Francisco",
                            "name:ru": "Сан-Франциско",
                            "name:sc": "San Francisco",
                            "name:sh": "San Francisco",
                            "name:si": "සැන් ෆ්‍රැන්සිස්කෝ",
                            "name:sk": "San Francisco",
                            "name:sl": "San Francisco",
                            "name:so": "San Fransisko",
                            "name:sq": "San Francisco",
                            "name:sr": "Сан Франциско",
                            "name:sv": "San Francisco",
                            "name:sw": "San Francisco",
                            "name:ta": "சான் பிரான்சிஸ்கோ",
                            "name:te": "శాన్ ఫ్రాన్సిస్కో",
                            "name:th": "ซานฟรานซิสโก",
                            "name:tl": "San Francisco",
                            "name:tr": "San Francisco",
                            "name:tt": "Сан-Франциско",
                            "name:tw": "San Francisco",
                            "name:ty": "San Francisco",
                            "name:ug": "San Fransisko",
                            "name:uk": "Сан-Франциско",
                            "name:ur": "سان فرانسسکو",
                            "name:uz": "San Fransisko",
                            "name:vi": "Cựu Kim Sơn",
                            "name:vo": "San Francisco",
                            "name:yi": "סאן פראנציסקא",
                            "name:yo": "San Francisco",
                            "name:zh": "旧金山;舊金山;三藩市",
                            "alt_name": "San Fran",
                            "boundary": "administrative",
                            "name:als": "San Francisco",
                            "name:arz": "سان فرانسيسكو",
                            "name:ast": "San Francisco",
                            "name:azb": "سان فرانسیسکو",
                            "name:bar": "San Francisco",
                            "name:bpy": "সান ফ্রান্সিসকো কাউন্টি",
                            "name:cdo": "Gô-gĭng-săng",
                            "name:ceb": "San Francisco",
                            "name:chy": "San Francisco",
                            "name:ckb": "سان فرانسیسکۆ",
                            "name:cmn": "舊金山;旧金山",
                            "name:diq": "San Francisco",
                            "name:dty": "सान फ्रान्सिस्को",
                            "name:eml": "San Francisco",
                            "name:ext": "San Franciscu",
                            "name:gan": "舊金山",
                            "name:hak": "San Francisco",
                            "name:haw": "Kapalakiko",
                            "name:hyw": "Սան Ֆրանսիսքօ",
                            "name:ilo": "San Francisco",
                            "name:inh": "Сан-Франциско",
                            "name:kab": "San Francisco",
                            "name:kbp": "Sanfransiskoo",
                            "name:krc": "Сан-Франциско",
                            "name:lad": "San Francisco",
                            "name:lmo": "San Francisco",
                            "name:lrc": "سان‌ فرانسیسکو",
                            "name:mhr": "Сан-Франциско",
                            "name:mrj": "Сан-Франциско",
                            "name:nah": "San Francisco",
                            "name:nan": "San Francisco",
                            "name:nds": "San Francisco",
                            "name:new": "स्यान फ्रान्सिस्को",
                            "name:pam": "San Francisco",
                            "name:pap": "San Francisco",
                            "name:pdc": "San Francisco",
                            "name:pms": "San Francisco",
                            "name:pnb": "سان فرانسسکو",
                            "name:rmy": "San Francisco",
                            "name:sah": "Сан Франсиско",
                            "name:scn": "San Franciscu",
                            "name:sco": "San Francisco",
                            "name:stq": "San Francisco",
                            "name:szl": "San Francisco",
                            "name:vec": "San Francisco",
                            "name:vep": "San Francisko",
                            "name:war": "San Francisco",
                            "name:wuu": "舊金山",
                            "name:xmf": "სან-ფრანცისკო",
                            "name:yue": "三藩市",
                            "wikidata": "Q62",
                            "wikipedia": "en:San Francisco",
                            "population": "873965",
                            "short_name": "SF",
                            "admin_level": "6",
                            "alt_name:en": "San Fran",
                            "alt_name:vi": "San Francisco",
                            "alt_name:zh": "聖弗朗西斯科;圣弗朗西斯科",
                            "border_type": "county;city",
                            "county:ansi": "075",
                            "county:name": "San Francisco",
                            "loc_name:vi": "Xăng Phăng",
                            "alt_name:cmn": "聖弗朗西斯科;圣弗朗西斯科",
                            "name:cbk-zam": "San Francisco",
                            "name:zh-Hans": "旧金山",
                            "name:zh-Hant": "舊金山;三藩市",
                            "county:abbrev": "SFO",
                            "name:cmn-Hans": "旧金山",
                            "name:cmn-Hant": "舊金山",
                            "official_name": "City and County of San Francisco",
                            "short_name:en": "SF",
                            "nist:fips_code": "6075",
                            "contact:website": "https://sfgov.org",
                            "name:zh-Hant-HK": "三藩市",
                            "name:zh-Hant-TW": "舊金山",
                            "nist:state_fips": "6",
                            "population:date": "2020",
                            "alt_name:zh-Hans": "圣弗朗西斯科",
                            "alt_name:zh-Hant": "聖弗朗西斯科",
                            "official_name:en": "City and County of San Francisco",
                            "official_name:es": "Ciudad y Condado de San Francisco",
                            "official_name:zh": "旧金山市县;舊金山市郡;三藩市市縣",
                            "alt_name:cmn-Hans": "圣弗朗西斯科",
                            "alt_name:cmn-Hant": "聖弗朗西斯科",
                            "official_name:yue": "三藩市市縣",
                            "official_name:zh-Hans": "旧金山市县",
                            "official_name:zh-Hant": "舊金山市郡;三藩市市縣",
                            "official_name:cmn-Hans": "旧金山市县",
                            "official_name:cmn-Hant": "舊金山市郡",
                            "official_name:zh-Hant-HK": "三藩市市縣",
                            "official_name:zh-Hant-TW": "舊金山市郡",
                        },
                    }
                ],
            }
        }

    # pylint: enable=line-too-long
