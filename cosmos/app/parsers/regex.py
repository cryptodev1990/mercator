"""Regular expression parsers."""
import re
from typing import Any, Dict, Optional

from .exceptions import QueryParseError

QUERY_PAT = re.compile(
    r"^(?:get )?(?P<subject>.*?)(?:\s+(?P<predicate>(not\s+)?in)\s+(?P<object>.*))?$"
)


def parse(query: str) -> Optional[Dict[str, Any]]:
    """Parse query."""
    m = QUERY_PAT.search(query)
    if not m:
        raise QueryParseError(query)

    model = "regex-0.0.2"
    pred = m.group("predicate")
    sprel = None
    if pred:
        pred = pred.strip()
        if pred == "not in":
            sprel = "disjoint"
        elif pred == "in":
            sprel = "covered_by"
        else:
            raise QueryParseError(query)
    if sprel:
        return {
            "intent": sprel,
            "args": {
                "subject": {
                    "text": m.group("subject"),
                    "start": m.start("subject"),
                    "end": m.end("subject"),
                },
                "predicate": {
                    "text": m.group("predicate"),
                    "start": m.start("predicate"),
                    "end": m.end("predicate"),
                },
                "object": {
                    "text": m.group("object"),
                    "start": m.start("object"),
                    "end": m.end("object"),
                },
            },
            "model": model,
        }
    return {
        "intent": "search",
        "args": {
            "subject": {
                "text": m.group("subject"),
                "start": m.start("subject"),
                "end": m.end("subject"),
            }
        },
        "model": model,
    }
