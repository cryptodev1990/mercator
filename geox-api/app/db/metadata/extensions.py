from alembic_utils.pg_extension import PGExtension
from typing import List

extensions = ["postgis", "pg_trgm"]

entities: List[PGExtension] = [
    PGExtension(
    schema="public",
    signature=ext
) for ext in extensions]

