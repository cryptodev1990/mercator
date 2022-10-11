from textwrap import dedent
from typing import List

from alembic_utils.pg_policy import PGPolicy

__all__ = ["shapes_same_org", "namespaces_same_org"]
entities: List[PGPolicy] = []

_same_org_policy = dedent(
    """
    AS PERMISSIVE
    FOR ALL
    TO app_user
    USING (app_user_org() = organization_id)
    WITH CHECK (app_user_org() = organization_id)
"""
).strip()

shapes_same_org = PGPolicy(
    schema="public",
    signature="same_org",
    on_entity="public.shapes",
    definition=_same_org_policy,
)

entities.append(shapes_same_org)

namespaces_same_org = PGPolicy(
    schema="public",
    signature="same_org",
    on_entity="public.namespaces",
    definition=_same_org_policy,
)

entities.append(namespaces_same_org)
