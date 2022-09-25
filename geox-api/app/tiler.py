from fastapi import Depends, FastAPI
from timvt.db import PostgresSettings as TimVTPostgresSettings
from timvt.db import close_db_connection, connect_to_db, register_table_catalog
from timvt.factory import VectorTilerFactory
from timvt.layer import FunctionRegistry

from app.core.config import get_tiler_settings
from app.dependencies import verify_token


def add_tiler_routes(app: FastAPI) -> None:
    # Add Function registry to the application state
    app.state.timvt_function_catalog = FunctionRegistry()

    # Register Start/Stop application event handler to setup/stop the database connection
    # and populate `app.state.table_catalog`

    @app.on_event("startup")
    async def startup_event():
        """Application startup: register the database connection and create table list."""
        pg_settings = get_tiler_settings()
        await connect_to_db(app, pg_settings)
        await register_table_catalog(app)

    @app.on_event("shutdown")
    async def shutdown_event():
        """Application shutdown: de-register the database connection."""
        await close_db_connection(app)

    # Register endpoints.
    mvt_tiler = VectorTilerFactory(
        with_tables_metadata=True,
        # add Functions metadata endpoints (/functions.json, /{function_name}.json)
        with_functions_metadata=False,
        with_viewer=True,
    )

    app.include_router(
        mvt_tiler.router, tags=["tiles"], dependencies=[Depends(verify_token)]
    )
