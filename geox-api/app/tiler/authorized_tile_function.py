from typing import Any

import morecantile
from buildpg import Func, asyncpg, clauses, render
from timvt import layer

from app.core.stats import time_db_query


class AuthorizedTileFunction(layer.Function):
    """Custom Function Layer: SQL function takes xyz input and an organization ID"""

    async def get_tile(
        self,
        pool: asyncpg.BuildPgPool,
        tile: morecantile.Tile,
        tms: morecantile.TileMatrixSet,  # tms won't be used here
        **kwargs: Any,
    ):
        """Custom get_tile method which translates a request for an MVT tile into a SQL query.
        See generate_shape_tile.sql for the SQL that actually executes on each MVT tile request.

        We moved this to a db migration on Jan 9 2023, since we identified
        that the function was getting created/replaced needlessly
        """

        async with pool.acquire() as conn:
            transaction = conn.transaction()
            await transaction.start()

            # with time_db_query("get_tile_sql"):
            #     import time
            #     start = time.time()
            #     await conn.execute(self.sql)
            #     end = time.time() - start
            #     print(end)

            sql_query = clauses.Select(
                Func(
                    self.function_name,
                    ":z",
                    ":x",
                    ":y",
                    ":filter_organization_id",
                    ":namespace_ids",
                ),
            )
            q, p = render(
                str(sql_query),
                x=tile.x,
                y=tile.y,
                z=tile.z,
                filter_organization_id=str(kwargs["organization_id"]),
                namespace_ids=kwargs.get("namespace_ids"),
            )

            # execute the query
            with time_db_query("get_tile_fetchval"):
                content = await conn.fetchval(q, *p)

            # rollback
            await transaction.rollback()

        return content
