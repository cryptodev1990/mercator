from alembic_utils.pg_function import PGFunction
from textwrap import dedent

__all__ = ["create_default_organization"]

create_default_organization = PGFunction(
    schema='public',
    signature='create_default_organization()',
    definition=dedent("""
    returns trigger
    LANGUAGE plpgsql
    AS $function$
        DECLARE
            new_organization_id UUID;
        BEGIN
            INSERT INTO organizations (name, created_at, updated_at, is_personal) VALUES
            (
                COALESCE(NEW."nickname" || ' Workspace', NEW.email || ' - Default Workspace'),
                NOW(),
                NOW(),
                TRUE
            ) RETURNING id INTO new_organization_id;
            INSERT INTO organization_members (organization_id, user_id, created_at, updated_at, active) VALUES (new_organization_id, NEW."id", NOW(), NOW(), TRUE);
            RETURN NEW;
        END;
    $function$
    """.strip()))
