
from alembic_utils.pg_function import PGFunction
from textwrap import dedent

__all__ = ["remove_orphaned_organizations"]

remove_orphaned_organizations = PGFunction(
    schema="public",
    signature="remove_orphaned_organizations()",
    definition=dedent("""
    returns trigger
    language plpgsql
    AS
    $function$
        BEGIN
            DELETE FROM organizations WHERE id NOT IN (SELECT DISTINCT organization_id FROM organization_members);
            RETURN OLD;
        END;
    $function$
    """.strip()))
