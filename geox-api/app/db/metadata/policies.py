from alembic_utils.pg_policy import PGPolicy
from typing import List
from textwrap import dedent

__all__ = ["shapes_same_org"]
entities: List[PGPolicy] = []

shapes_same_org = PGPolicy(
    schema="public",
    signature="same_org",
    on_entity="public.shapes",
    definition=dedent("""
    AS PERMISSIVE
    FOR ALL
    TO app_user
    USING (app_user_org() = organization_id)
    WITH CHECK (app_user_org() = organization_id)
    """).strip())

entities.append(shapes_same_org)