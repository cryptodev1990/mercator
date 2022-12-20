"""Autocomplete API"""


from app.core.config import get_settings
from fast_autocomplete import AutoComplete
from fastapi import APIRouter, Query
from pydantic import NonNegativeInt  # pylint: disable=no-name-in-module
from typing import List


QUERY_MAX_SIZE = 5
router = APIRouter(prefix="")


def _get_autocomplete():
    settings = get_settings()
    autocomplete_path = settings.resource("autocomplete")

    return AutoComplete(words={
        i: {}
        for i in open(autocomplete_path).read().split('\n')
    })


_autocomplete = _get_autocomplete()


@router.get(
    "/search",
    response_model=List[str],
    responses={"400": {"description": "Unable to parse query."}},
)
async def _query(
    text: str = Query(..., example="Shops near", description="Incomplete text."),
    limit: NonNegativeInt = Query(QUERY_MAX_SIZE, description="Maximum number of results to return"),
) -> List[str]:
    """Autocomplete endpoint for text search queries.
    """

    size = limit if limit <= QUERY_MAX_SIZE else QUERY_MAX_SIZE
    results = _autocomplete.search(text, max_cost=3, size=limit)

    return [j for i in results for j in i]
