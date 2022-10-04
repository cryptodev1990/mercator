"""update app_user_org

Revision ID: 710a857ba43b
Revises: 3a5e81cddc7e
Create Date: 2022-10-04 14:31:16.872193

"""
from alembic import op
import sqlalchemy as sa
from alembic_utils.pg_function import PGFunction
from sqlalchemy import text as sql_text

# revision identifiers, used by Alembic.
revision = '710a857ba43b'
down_revision = '3a5e81cddc7e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    public_app_user_org = PGFunction(
        schema="public",
        signature="app_user_org()",
        definition="RETURNS UUID as\n  $$\n    SELECT nullif(current_setting('app.user_org', TRUE), '') :: UUID;\n  $$ language SQL"
    )
    op.replace_entity(public_app_user_org)


def downgrade() -> None:
    public_app_user_org = PGFunction(
        schema="public",
        signature="app_user_org()",
        definition='returns uuid\n LANGUAGE sql\n SECURITY DEFINER\nAS $function$\n        SELECT organization_id\n        FROM organization_members\n        WHERE deleted_at IS NULL\n            AND active\n            AND user_id = app_user_id()\n        $function$'
    )
    op.replace_entity(public_app_user_org)
