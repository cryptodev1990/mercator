"""Remove remove_orphaned_organizations trigger

Revision ID: 0b14e3fc512e
Revises: 41877eca4e70
Create Date: 2022-10-07 10:06:18.380976

"""
from alembic import op
import sqlalchemy as sa
from alembic_utils.pg_function import PGFunction
from sqlalchemy import text as sql_text
from alembic_utils.pg_trigger import PGTrigger
from sqlalchemy import text as sql_text

# revision identifiers, used by Alembic.
revision = '0b14e3fc512e'
down_revision = '41877eca4e70'
branch_labels = None
depends_on = None


def upgrade() -> None:
    public_users_users_delete_trigger = PGTrigger(
        schema="public",
        signature="users_delete_trigger",
        on_entity="public.users",
        is_constraint=False,
        definition='AFTER DELETE ON public.users FOR EACH ROW EXECUTE FUNCTION remove_orphaned_organizations()'
    )
    op.drop_entity(public_users_users_delete_trigger)

    public_remove_orphaned_organizations = PGFunction(
        schema="public",
        signature="remove_orphaned_organizations()",
        definition='returns trigger\n LANGUAGE plpgsql\nAS $function$\n          BEGIN\n            DELETE FROM organizations WHERE id NOT IN (SELECT DISTINCT organization_id FROM organization_members);\n            RETURN OLD;\n          END;\n        $function$'
    )
    op.drop_entity(public_remove_orphaned_organizations)

def downgrade() -> None:
    public_remove_orphaned_organizations = PGFunction(
        schema="public",
        signature="remove_orphaned_organizations()",
        definition='returns trigger\n LANGUAGE plpgsql\nAS $function$\n          BEGIN\n            DELETE FROM organizations WHERE id NOT IN (SELECT DISTINCT organization_id FROM organization_members);\n            RETURN OLD;\n          END;\n        $function$'
    )
    op.create_entity(public_remove_orphaned_organizations)


    public_users_users_delete_trigger = PGTrigger(
        schema="public",
        signature="users_delete_trigger",
        on_entity="public.users",
        is_constraint=False,
        definition='AFTER DELETE ON public.users FOR EACH ROW EXECUTE FUNCTION remove_orphaned_organizations()'
    )
    op.create_entity(public_users_users_delete_trigger)

