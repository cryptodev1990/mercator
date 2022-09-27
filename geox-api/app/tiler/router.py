import os

from fastapi import Depends, FastAPI
from timvt.db import close_db_connection, connect_to_db, register_table_catalog
from timvt.layer import FunctionRegistry

from app.core.config import get_tiler_settings
from app.dependencies import verify_token
from app.tiler.authorized_tile_function import AuthorizedTileFunction
from app.tiler.authorized_tile_router import router

dir = os.path.dirname(__file__)


def add_tiler_routes(app: FastAPI) -> None:
    # Add Function registry to the application state
    app.state.timvt_function_catalog = FunctionRegistry()

    # Register Start/Stop application event handler to setup/stop the database connection
    # and populate `app.state.table_catalog`

    @app.on_event("startup")
    async def startup_event():
        """Application startup: register the database connection and create table list."""
        pg_settings = get_tiler_settings()
        await connect_to_db(app, pg_settings)  # noqa
        await register_table_catalog(app)

    @app.on_event("shutdown")
    async def shutdown_event():
        """Application shutdown: de-register the database connection."""
        await close_db_connection(app)

    app.state.timvt_function_catalog.register(
        AuthorizedTileFunction.from_file(
            id="generate_shape_tile",
            infile=os.path.join(dir, "generate_shape_tile.sql"),
        )
    )

    app.include_router(router, tags=["tiles"], dependencies=[Depends(verify_token)])
