"""Rule based parser using SpaCy."""
import logging
from datetime import timedelta
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

import spacy
from pint import Quantity, UnitRegistry
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module
from spacy.tokens import Doc, Span, Token
from spacy.util import filter_spans

from app.parsers.dist import parse as parse_distance
from app.parsers.time import parse as parse_time

from .exceptions import QueryParseError

logger = logging.getLogger(__name__)


ureg = UnitRegistry()


def _quantity_to_dict(quantity: Quantity) -> dict[str, Any]:
    return {"magnitude": quantity.magnitude, "units": str(quantity.units)}


class _LocalModel(BaseModel):
    """Local pydantic model for this module."""

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True
        custom_encoders = {Quantity: _quantity_to_dict}


# pylint: disable=invalid-name
class TravelMethod(str, Enum):
    """Travel methods used in isochrones."""

    drive = "drive"
    walk = "walk"
    bike = "bike"


# pylint: enable=invalid-name


class Place(_LocalModel):
    """Represents a place."""

    # NOTE: the Literal[...] = Field(...) is redundant, but it seems to be needed to get
    # Field(..., discriminator=...) to work.
    type: Literal["place"] = Field("place", const=True)
    value: List[str]

    def __str__(self) -> str:
        return " ".join(self.value)


class NamedPlace(_LocalModel):
    """Named place."""

    type: Literal["named_place"] = Field("named_place", const=True)
    value: List[str]

    def __str__(self) -> str:
        return " ".join(self.value)


class _SpatialRelationship(_LocalModel):
    subject: Union[Place, NamedPlace]
    object: Union[Place, NamedPlace]


class SpRelCoveredBy(_SpatialRelationship):
    """Spatial relationship of X is covered by Y."""

    type: Literal["covered_by"] = Field("covered_by", const=True)

    def __str__(self) -> str:
        return " ".join([str(self.subject), "IN", str(self.object)])


class SpRelDisjoint(_SpatialRelationship):
    """Spatial relationship of X disjoint Y."""

    type: Literal["disjoint"] = Field("disjoint", const=True)

    def __str__(self) -> str:
        return " ".join([str(self.subject), "NOT IN", str(self.object)])


class SpRelWithinDistOf(_SpatialRelationship):
    """Spatial relationship of X within D distance of Y."""

    type: Literal["within_dist_of"] = Field("within_dist_of", const=True)
    distance: float = Field(..., ge=0, description="Distance in meters")

    def __str__(self) -> str:
        return " ".join(
            [
                str(self.subject),
                "LESS THAN",
                str(Quantity(self.distance, "meters")),
                "FROM",
                str(self.object),
            ]
        )


class SpRelOutsideDistOf(_SpatialRelationship):
    """Spatial relationship of X more than D distance of Y."""

    type: Literal["outside_dist_of"] = Field("outside_dist_of", const=True)
    distance: float = Field(..., ge=0, description="Distance in meters")

    def __str__(self) -> str:
        return " ".join(
            [
                str(self.subject),
                "MORE THAN",
                str(Quantity(self.distance, "meters")),
                "FROM",
                str(self.object),
            ]
        )


NEAR_DISTANCE = 1609.344
"""Constant used to determine the distance between two objects that is near."""


class SpRelNear(_SpatialRelationship):
    """Spatial relationship of X near Y."""

    type: Literal["near"] = Field("near", const=True)
    distance: float = Field(NEAR_DISTANCE, ge=0, description="Distance in meters")

    def __str__(self) -> str:
        return " ".join([str(self.subject), "NEAR", str(self.object)])


class SpRelNotNear(_SpatialRelationship):
    """Spatial relationship of X not near Y."""

    type: Literal["not_near"] = Field("not_near", const=True)
    distance: float = Field(NEAR_DISTANCE, ge=0, description="Distance in meters")

    def __str__(self) -> str:
        return " ".join([str(self.subject), "NOT NEAR", str(self.object)])


class SpRelWithinTimeOf(_SpatialRelationship):
    """Spatial relationship of X within D time of Y."""

    type: Literal["within_time_of"] = Field("within_time_of", const=True)
    duration: timedelta
    method: TravelMethod = TravelMethod.drive

    def __str__(self) -> str:
        return " ".join(
            [str(self.subject), "LESS THAN", str(self.duration), "FROM", str(self.object)]
        )


class SpRelOutsideTimeOf(_SpatialRelationship):
    """Spatial relationship of X greater than D time from Y."""

    type: Literal["outside_time_of"] = Field("outside_time_of", const=True)
    duration: timedelta
    method: TravelMethod = TravelMethod.drive

    def __str__(self) -> str:
        return " ".join(
            [str(self.subject), "MORE THAN", str(self.duration), "FROM", str(self.object)]
        )


class Buffer(_LocalModel):
    """Buffer around object."""

    type: Literal["buffer"] = Field("buffer", const=True)
    object: Union[Place, NamedPlace]
    distance: float = Field(..., ge=0, description="Distance in meters")

    def __str__(self) -> str:
        return " ".join(
            ["BUFFER OF", str(Quantity(self.distance, "meters")), "AROUND", str(self.object)]
        )


class Isochrone(_LocalModel):
    """Isochrone around an object."""

    type: Literal["isochrone"] = Field("isochrone", const=True)
    object: Union[Place, NamedPlace]
    duration: timedelta
    method: TravelMethod = TravelMethod.drive

    def __str__(self) -> str:
        return " ".join(["ISOCHRONE OF", str(self.duration), "AROUND", str(self.object)])


class Route(_LocalModel):
    """Route between two places."""

    type: Literal["route"] = Field("route", const=True)
    start: NamedPlace
    end: NamedPlace
    along: Union[Place, NamedPlace, None] = None
    method: TravelMethod = TravelMethod.drive

    def __str__(self) -> str:
        words = []
        if self.along:
            words = [str(self.along), "ALONG"]
        words += ["ROUTE FROM", str(self.start), "TO", str(self.end)]
        return " ".join(words)


QueryIntents = Union[
    Route,
    Isochrone,
    Buffer,
    SpRelCoveredBy,
    SpRelDisjoint,
    SpRelWithinDistOf,
    SpRelOutsideDistOf,
    SpRelNear,
    SpRelNotNear,
    SpRelWithinTimeOf,
    SpRelOutsideTimeOf,
    Place,
    NamedPlace,
]


class ParsedQuery(_LocalModel):
    """Route between two places."""

    value: QueryIntents = Field(..., description="Query intent", discriminator="type")
    text: str
    tokens: List[str]

    def __str__(self) -> str:
        return str(self.value)


NOUN_POS = {"NOUN", "PROPN"}
"""Noun-like part of speech tags."""

NOUN_TAGS = {"NN", "NNS", "NNP", "NNPS"}
"""Noun-like fine-grained part of speech tags."""


# Initialize the pipeline
nlp = spacy.load("en_core_web_sm")

KILOMETERS = ["km", "kilometers", "kilometer", "kilometres", "kilometre"]
METERS = ["m", "meters", "meter", "metres", "metre"]
MILES = ["mi", "miles", "mile"]
DIST_UNITS = KILOMETERS + METERS + MILES

DIST_UNIT_PAT = "(?:" + "|".join(DIST_UNITS) + ")"
NUM_PAT = r"(?:\d+(?:\.\d+)?|\.\d+)"

dist_patterns = [
    [{"LIKE_NUM": True}, {"LOWER": {"IN": DIST_UNITS}}],
    [{"TEXT": {"REGEX": f"^{NUM_PAT}{DIST_UNIT_PAT}$"}}],
]

HOURS = ["hours", "hour", "hrs", "hr", "h"]
MINUTES = ["minutes", "minute", "mins", "min", "m"]
SECONDS = ["seconds", "second", "secs", "sec", "s"]

duration_patterns = [
    *[
        [{"LIKE_NUM": True, "ENT_TYPE": "TIME"}, {"LOWER": {"IN": unit}}]
        for unit in [HOURS, MINUTES, SECONDS]
    ],
    *[
        [
            {"LIKE_NUM": True, "ENT_TYPE": "TIME"},
            {"LOWER": {"IN": unit1}},
            {"POS": "CCONJ", "OP": "?"},
            {"LIKE_NUM": True, "ENT_TYPE": "TIME"},
            {"LOWER": {"IN": unit2}},
        ]
        for (unit1, unit2) in [(HOURS, MINUTES), (MINUTES, SECONDS), (HOURS, SECONDS)]
    ],
    *[
        [
            {"LIKE_NUM": True, "ENT_TYPE": "TIME"},
            {"LOWER": {"IN": unit1}},
            {"POS": "CCONJ", "OP": "?"},
            {"LIKE_NUM": True, "ENT_TYPE": "TIME"},
            {"LOWER": {"IN": unit2}},
            {"POS": "CCONJ", "OP": "?"},
            {"LIKE_NUM": True, "ENT_TYPE": "TIME"},
            {"LOWER": {"IN": unit3}},
        ]
        for (unit1, unit2, unit3) in [(HOURS, MINUTES, SECONDS)]
    ],
    [{"TEXT": {"REGEX": "^[0-9]{1,2}:[0-9]{2}(:[0-9]{2})?$"}, "ENT_TYPE": "TIME"}],
    [
        {"LIKE_NUM": True},
        {"LOWER": "h"},
        {"POS": "CCONJ", "OP": "?"},
        {"LIKE_NUM": True},
        {"LOWER": "m"},
    ],
    [
        {"LIKE_NUM": True},
        {"LOWER": "m"},
        {"POS": "CCONJ", "OP": "?"},
        {"LIKE_NUM": True},
        {"LOWER": "s"},
    ],
    [
        {"LIKE_NUM": True},
        {"LOWER": "h"},
        {"POS": "CCONJ", "OP": "?"},
        {"LIKE_NUM": True},
        {"LOWER": "s"},
    ],
    [{"TEXT": {"REGEX": "^[0-9]{1,2}:[0-9]{2}(:[0-9]{2})?$"}}],
]


entity_ruler = nlp.add_pipe(
    "entity_ruler", after="ner", config={"overwrite_ents": True, "validate": True}
)
entity_ruler.add_patterns(  # type: ignore
    [{"label": "DURATION", "pattern": pattern} for pattern in duration_patterns]
)
# pylint: disable=line-too-long
entity_ruler.add_patterns([{"label": "DISTANCE", "pattern": pattern} for pattern in dist_patterns])  # type: ignore
# pylint: enable=line-too-long

nlp.add_pipe("merge_entities", after="entity_ruler")


def _first_sentence(doc: Doc) -> Span:
    return next(doc.sents)


def _get_noun_chunk(tok: Token) -> Optional[Span]:
    for noun_chunk in tok.doc.noun_chunks:
        if noun_chunk.start <= tok.i < noun_chunk.end:
            return noun_chunk
    return None


# Requires the root of the dependency tree
def _get_main_noun(sent: Span) -> Optional[Token]:
    root = sent.root
    if root.pos_ in NOUN_POS:
        return root
    if root.pos_ == "VERB":
        # "Where are pubs in Oakland"
        for child in root.children:
            if child.pos_ in NOUN_POS:
                if child.dep_ in {"nsubj", "ccomp", "nsubjpass", "dobj"}:
                    return child
            if child.dep_ == "prep":
                if child.dep_ == "pobj" and child.pos_ in NOUN_POS:
                    return child
    # if no noun is found, then use the head of the first noun chunk in the sentence
    for chunk in sent.noun_chunks:
        return chunk.root
    return None


def _get_main_noun_chunk(sent: Span) -> Optional[Span]:
    main_noun = _get_main_noun(sent)
    if main_noun:
        return _get_noun_chunk(main_noun)
    return None


LOCATE_SYNONYMS = ["locate", "found"]

patterns = {}
patterns["IN"] = [
    [{"LEMMA": {"IN": LOCATE_SYNONYMS}, "OP": "?"}, {"DEP": "prep", "LOWER": "in"}],
    [{"LEMMA": {"IN": LOCATE_SYNONYMS}, "OP": "?"}, {"DEP": "prep", "LOWER": "within"}],
    [
        {"LEMMA": {"IN": LOCATE_SYNONYMS}, "OP": "?"},
        {"DEP": "prep", "LOWER": "inside"},
        {"DEP": "prep", "LOWER": "of", "OP": "?"},
    ],
]

patterns["NOT_IN"] = [
    [
        {"DEP": "neg"},
        {"LEMMA": {"IN": LOCATE_SYNONYMS}, "OP": "?"},
        {"DEP": "prep", "LOWER": "in"},
    ],
    [
        {"DEP": "neg"},
        {"LEMMA": {"IN": LOCATE_SYNONYMS}, "OP": "?"},
        {"DEP": "prep", "LOWER": "within"},
    ],
    [
        {"DEP": "neg"},
        {"LEMMA": {"IN": LOCATE_SYNONYMS}, "OP": "?"},
        {"DEP": "prep", "LOWER": "inside"},
        {"DEP": "prep", "LOWER": "of", "OP": "?"},
    ],
    [{"LEMMA": "outside", "DEP": "prep"}, {"DEP": "prep", "LOWER": "of", "OP": "?"}],
]

patterns["WITHIN_DIST_OF"] = [
    [
        {"LEMMA": {"IN": ["in", "inside", "within"]}, "TAG": "IN", "DEP": "prep"},
        {"ENT_TYPE": "DISTANCE", "DEP": "pobj"},
        {"TAG": "IN", "DEP": "prep", "OP": "?"},
    ]
]

patterns["OUTSIDE_DIST_OF"] = [
    [
        {"DEP": "neg"},
        {"LEMMA": {"IN": ["in", "inside", "within"]}, "TAG": "IN", "DEP": "prep"},
        {"ENT_TYPE": "DISTANCE", "DEP": "pobj"},
        {"TAG": "IN", "DEP": "prep", "OP": "?"},
    ],
    [
        {"LEMMA": {"IN": ["outside", "out"]}, "TAG": "IN", "DEP": "prep"},
        {"ENT_TYPE": "DISTANCE", "DEP": "pobj"},
        {"TAG": "IN", "DEP": "prep", "OP": "?"},
    ],
]

patterns["WITHIN_TIME_OF"] = [
    [
        {"LEMMA": {"IN": ["in", "inside", "within"]}, "TAG": "IN", "DEP": "prep"},
        {"DEP": "prep", "OP": "*"},
        {"ENT_TYPE": "DURATION", "DEP": "pobj"},
        {"TAG": "IN", "DEP": "prep", "OP": "?"},
    ]
]

patterns["OUTSIDE_TIME_OF"] = [
    [
        {"DEP": "neg"},
        {"LEMMA": {"IN": ["in", "inside", "within"]}, "TAG": "IN", "DEP": "prep"},
        {"DEP": "prep", "OP": "*"},
        {"ENT_TYPE": "DURATION", "DEP": "pobj"},
        {"TAG": "IN", "DEP": "prep", "OP": "?"},
    ],
    [
        {"LEMMA": {"IN": ["outside", "out"]}, "TAG": "IN", "DEP": "prep"},
        {"DEP": "prep", "OP": "*"},
        {"ENT_TYPE": "DURATION", "DEP": "pobj"},
        {"TAG": "IN", "DEP": "prep", "OP": "?"},
    ],
]

patterns["BUFFER"] = [
    # buffer of {distance} around
    [
        {"LEMMA": {"IN": ["buffer"]}},
        {"TAG": "IN", "DEP": "prep", "OP": "?"},
        {"ENT_TYPE": "DISTANCE"},
        {"LEMMA": "around"},
    ],
    # {distance} buffer around
    [
        {"ENT_TYPE": "DISTANCE"},
        {"LEMMA": {"IN": ["buffer"]}},
        {"ENT_TYPE": "DISTANCE"},
        {"LEMMA": "around"},
    ],
]

patterns["ISOCHRONE"] = [
    # buffer of {duration} around
    [
        {"LEMMA": {"IN": ["buffer", "isochrone"]}},
        {"TAG": "IN", "DEP": "prep", "OP": "?"},
        {"ENT_TYPE": "DURATION"},
        {"LEMMA": "around", "OP": "?"},
    ],
    # {duration} buffer around
    [
        {"ENT_TYPE": "DURATION"},
        {"LEMMA": {"IN": ["buffer", "isochrone"]}},
        {"LEMMA": "around", "OP": "?"},
    ],
]

patterns["NEAR"] = [
    # buffer of {duration} around
    [
        {"LEMMA": {"IN": ["near", "nearby", "close"]}},
        {"POS": "ADP", "DEP": "prep", "OP": "?"},
    ]
]

patterns["NOT_NEAR"] = [
    # buffer of {duration} around
    [
        {"DEP": "neg"},
        {"LEMMA": {"IN": ["near", "nearby", "close"]}},
        {"POS": "ADP", "DEP": "prep", "OP": "?"},
    ]
]

patterns["ROUTE"] = [
    # buffer of {duration} around
    [{"POS": "NOUN", "LEMMA": "route"}]
]

span_ruler = nlp.add_pipe("span_ruler", config={"spans_key": "cosmos"})
for _label, _pat in patterns.items():
    span_ruler.add_patterns([{"label": _label, "pattern": p} for p in _pat])  # type: ignore
del patterns


def placemaker(span: Span) -> NamedPlace | Place:
    """Generates a NamedPlace or Place object from a Span."""
    if span.root.ent_type_ == "GPE":
        return NamedPlace.parse_obj({"value": [str(span.root)]})
    return Place.parse_obj({"value": [str(t) for t in span]})


def _get_prep_args(span: Span) -> dict[str, NamedPlace | Place]:
    root = span.root
    subj = None
    for ancestor in reversed(list(root.ancestors)):
        if ancestor.pos_ in NOUN_POS:
            subj = _get_noun_chunk(ancestor)
            break
    if subj is None:
        raise QueryParseError("No subject found")
    obj = None
    for child in root.subtree:
        if child not in span and child.pos_ in NOUN_POS:
            obj = _get_noun_chunk(child)
    if obj is None:
        raise QueryParseError("No object found")
    return {"subject": placemaker(subj), "object": placemaker(obj)}


def _sum_dist_in_m(quantities: List[Quantity]) -> float:
    return float(sum(q.to("meter").magnitude for q in quantities))


def _get_within_dist_args(span: Span) -> Dict[str, Any]:
    root = span.root
    subj = None
    for ancestor in reversed(list(root.ancestors)):
        if ancestor.pos_ in NOUN_POS:
            subj = _get_noun_chunk(ancestor)
            break
    if subj is None:
        raise QueryParseError("No subject found")
    dist = None
    for tok in span:
        if tok.ent_type_ == "DISTANCE":
            dist = tok
    if dist is None:
        raise QueryParseError("No object found")
    obj = None
    for tok in span.subtree:
        if tok not in span and tok.pos_ in NOUN_POS:
            obj = _get_noun_chunk(tok)
    if obj is None:
        raise QueryParseError("No object found")
    return {
        "subject": placemaker(subj),
        "object": placemaker(obj),
        "distance": _sum_dist_in_m(parse_distance(str(dist))),
    }


def _get_within_time_args(span: Span) -> Dict[str, Any]:
    root = span.root
    subj = None
    for ancestor in reversed(list(root.ancestors)):
        if ancestor.pos_ in NOUN_POS:
            subj = _get_noun_chunk(ancestor)
            break
    if subj is None:
        raise QueryParseError("No subject found")
    duration = None
    for tok in span:
        if tok.ent_type_ == "DURATION":
            duration = tok
    if duration is None:
        raise QueryParseError("No duation found")
    obj = None
    for tok in span.subtree:
        if tok not in span and tok.pos_ in NOUN_POS:
            obj = _get_noun_chunk(tok)
    if obj is None:
        raise QueryParseError("No object found")
    return {
        "subject": placemaker(subj),
        "object": placemaker(obj),
        "duration": parse_time(str(duration)),
    }


def _get_buffer_dist_args(span: Span) -> Dict[str, Any]:
    obj = None
    for tok in span.subtree:
        if tok not in span and tok.pos_ in NOUN_POS:
            obj = _get_noun_chunk(tok)
    dist = None
    for tok in span:
        if tok.ent_type_ == "DISTANCE":
            dist = tok
    if obj is None:
        raise QueryParseError("No object found")
    if dist is None:
        raise QueryParseError("No distance found")
    return {"object": placemaker(obj), "distance": _sum_dist_in_m(parse_distance(str(dist)))}


def _get_buffer_time_args(span: Span) -> Dict[str, Any]:
    obj = None
    for tok in span.subtree:
        if tok not in span and tok.pos_ in NOUN_POS:
            obj = _get_noun_chunk(tok)
    duration = None
    for tok in span:
        if tok.ent_type_ == "DURATION":
            duration = tok
    if obj is None:
        raise QueryParseError("No object found")
    if duration is None:
        raise QueryParseError("No object found")
    return {"object": placemaker(obj), "duration": parse_time(str(duration))}


def _get_route_args(span: Span) -> Dict[str, Any]:
    root = span.root
    start = end = along = None
    doc = span.doc
    # Try looking for start and end after the span
    for tok in doc[span.end :]:
        if tok.lemma_ == "from":
            for grandchild in tok.children:
                if grandchild.dep_ == "pobj":
                    start = _get_noun_chunk(grandchild)
        elif tok.lemma_ == "to":
            for grandchild in tok.children:
                if grandchild.dep_ == "pobj":
                    end = _get_noun_chunk(grandchild)
    if not start or not end:
        remainder = Span(span.doc, span.end, len(doc))
        noun_chunks = []
        for nc in remainder.noun_chunks:
            if nc.start > span.end or nc.end < span.start:
                noun_chunks.append(nc)
        start = noun_chunks[0]
        end = noun_chunks[1]
    if root.head.lemma_ == "along":
        along = _get_noun_chunk(root.head.head)
    return {
        "start": placemaker(start),
        "end": placemaker(end),
        "along": placemaker(along) if along else None,
    }


def parse_default(span: Span) -> SpRelCoveredBy | NamedPlace | Place | None:
    """Parse the default case, where the span is a noun chunk."""
    noun_chunk = _get_main_noun_chunk(span)
    if noun_chunk:
        root_noun = noun_chunk.root
        in_obj = None
        if root_noun.ent_type_ != "GPE":
            for child in noun_chunk.root.children:
                if child.ent_type_ == "GPE" and child.pos_ == "PROPN":
                    in_obj = child
                    break
            if in_obj:
                subj = [str(tok) for tok in noun_chunk if tok != in_obj]
                return SpRelCoveredBy.parse_obj(
                    {
                        "subject": Place.parse_obj({"value": subj}),
                        "object": NamedPlace.parse_obj({"value": [str(in_obj)]}),
                    }
                )
        return placemaker(noun_chunk)
    return None


# pylint: disable=too-many-branches,too-many-locals
def parse(text: str) -> ParsedQuery:
    """Parse a text string into structured arguments that can be converted into SQL."""
    doc = nlp(text)
    sent = _first_sentence(doc)
    # retrieve spans
    doc.spans["cosmos"] = filter_spans(sorted(doc.spans["cosmos"], key=lambda x: (x.start, -x.end)))
    value: Optional[_LocalModel] = None
    for span in doc.spans["cosmos"]:
        label = doc.vocab.strings[span.label]
        if label == "IN":
            value = SpRelCoveredBy.parse_obj(_get_prep_args(span))
        elif label == "NOT_IN":
            value = SpRelDisjoint.parse_obj(_get_prep_args(span))
        elif label == "NEAR":
            value = SpRelNear.parse_obj(_get_prep_args(span))
        elif label == "NOT_NEAR":
            value = SpRelNotNear.parse_obj(_get_prep_args(span))
        elif label == "WITHIN_DIST_OF":
            value = SpRelWithinDistOf.parse_obj(_get_within_dist_args(span))
        elif label == "OUTSIDE_DIST_OF":
            value = SpRelOutsideDistOf.parse_obj(_get_within_dist_args(span))
        elif label == "WITHIN_TIME_OF":
            value = SpRelWithinTimeOf.parse_obj(_get_within_time_args(span))
        elif label == "OUTSIDE_TIME_OF":
            value = SpRelOutsideTimeOf.parse_obj(_get_within_time_args(span))
        elif label == "BUFFER":
            value = Buffer.parse_obj(_get_buffer_dist_args(span))
        elif label == "ISOCHRONE":
            value = Isochrone.parse_obj(_get_buffer_time_args(span))
        elif label == "ROUTE":
            value = Route.parse_obj(_get_route_args(span))
        else:
            raise QueryParseError(f"Unknown label {label}")
    if value is None:
        value = parse_default(sent)
    return ParsedQuery.parse_obj(
        {"tokens": [str(tok) for tok in sent], "text": str(doc), "value": value}
    )


# pylint: enable=too-many-branches,too-many-locals