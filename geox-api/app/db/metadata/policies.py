from textwrap import dedent
from typing import List

from alembic_utils.pg_policy import PGPolicy

__all__ = ["shapes_same_org"]
entities: List[PGPolicy] = []

shapes_same_org = PGPolicy(
    schema="public",
    signature="same_org",
    on_entity="public.shapes",
    definition=dedent(
        """
    AS PERMISSIVE
    FOR ALL
    TO app_user
    USING (app_user_org() = organization_id)
    WITH CHECK (app_user_org() = organization_id)
    """
    ).strip(),
)

entities.append(shapes_same_org)
