from textwrap import dedent

from alembic_utils.pg_trigger import PGTrigger

__all__ = [
    "users_insert_trigger",
    "organizations_insert_trigger",
]
entities = []

users_insert_trigger = PGTrigger(
    schema="public",
    signature="users_insert_trigger",
    on_entity="public.users",
    is_constraint=False,
    definition="AFTER INSERT ON public.users FOR EACH ROW EXECUTE FUNCTION create_default_organization()",
)
entities.append(users_insert_trigger)

organizations_insert_trigger = PGTrigger(
    schema="public",
    signature="organizations_insert_trigger",
    on_entity="public.organizations",
    is_constraint=False,
    definition=dedent(
        """
        AFTER INSERT ON public.organizations
        FOR EACH ROW
        EXECUTE FUNCTION create_default_namespace()
    """.strip()
    ),
)
entities.append(organizations_insert_trigger)
