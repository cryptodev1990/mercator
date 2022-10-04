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

exclude_objects = [
    # (type_, name)
    ("table", "spatial_ref_sys"),
    ("index", "organization_members_id_seq"),
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
    # Tables and columns include by default
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
