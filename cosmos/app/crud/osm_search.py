"""OSM search functions."""
import logging

from sqlalchemy.ext.asyncio import AsyncConnection

from app.core.config import get_settings

from app.core.datatypes import FeatureCollection

from app.parsers.intents import OpenAIDerivedIntent, ParsedQuery


settings = get_settings()

logger = logging.getLogger(__name__)


async def eval_query(
    arg: ParsedQuery,
    *,
    conn: AsyncConnection,
) -> FeatureCollection:
    """Evaluate a query"""
    expr = arg.value
    if isinstance(expr, OpenAIDerivedIntent):
        return await expr.intent.execute(**expr.args, conn=conn)
    else:
        raise ValueError("Only OpenAPI derived intents are supported at this time")
