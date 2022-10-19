from textwrap import dedent

from alembic_utils.pg_function import PGFunction

__all__ = ["create_default_namespace"]

create_default_namespace = PGFunction(
    schema="public",
    signature="create_default_namespace()",
    definition=dedent(
        """
    returns trigger
    LANGUAGE plpgsql
    AS $function$
        DECLARE
            new_organization_id UUID;
        BEGIN
            INSERT INTO namespaces (name, slug, organization_id)
            VALUES
            ('Default', 'default', NEW.id);

            RETURN NEW;
        END;
    $function$
    """.strip()
    ),
)
