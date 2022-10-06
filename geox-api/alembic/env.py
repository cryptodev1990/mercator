"""Alembic configuration."""
import pathlib

# Ensure that the app module can be reached
import sys
from logging.config import fileConfig

sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))

from sqlalchemy import engine_from_config, pool

from alembic import context
from app.core.config import get_settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)  # type: ignore

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None

from app.db.metadata import metadata

target_metadata = metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# ReplaceableEntity is the parent of all alembic_utils classes
from alembic_utils.replaceable_entity import register_entities, ReplaceableEntity
from alembic_utils.pg_grant_table import PGGrantTable

# Add new functions and procedures to this module
from app.db.metadata.functions import entities as function_entities
# Add new policies to this module
from app.db.metadata.policies import entities as policy_entities
# Add new extensions here
from app.db.metadata.extensions import entities as extension_entities
# Add new triggers to this module
from app.db.metadata.triggers import entities as trigger_entities
# Add new views to this module
from app.db.metadata.views import entities as view_entities
# Add new triggers to this module
from app.db.metadata.materialized_views import entities as materialized_view_entities

# Table grants still need to be managed directly in alembic

all_entities = [*function_entities, *policy_entities,  *extension_entities, *trigger_entities, *view_entities, *materialized_view_entities]

register_entities(all_entities)


exclude_objects = [
    # (type_, name)
    ("table", "spatial_ref_sys"), # created by postgis
    ("view", "public.geography_columns"),  # created by postgis
    ("view", "public.geometry_columns"), # created by postgis
]

def get_url() -> str:
    """Return the database URL."""
    settings = get_settings()
    if settings.sqlalchemy_database_uri is None:
        raise ValueError("Database URI is None")
    uri = str(settings.sqlalchemy_database_uri)
    return uri


def include_object(object, name, type_, reflected, compare_to):
    """Exclude objects from Alembic's consideration.

    - Tables and columns are included by default. Exclude them with ``exclude_objects``.
    - Other object types are excluded by default. Include them with ``include_objects``.

    """
    # Ignore grant table entities - too noisy to manage with alembic utils
    if isinstance(object, PGGrantTable):
        return False

    for obj_typ, obj_name in exclude_objects:
        if type_ == obj_typ and name == obj_name:
                return False
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.
    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    configuration = config.get_section(config.config_ini_section)
    if configuration is None:
        raise ValueError("Missing config_ini_section.")
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
