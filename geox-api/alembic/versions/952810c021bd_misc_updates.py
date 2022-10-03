"""Minor changes to columns

Revision ID: 952810c021bd
Revises: e4994335c3e0
Create Date: 2022-09-26 17:13:53.180495

Minor changes including comments on tables during removal of ORM.

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '952810c021bd'
down_revision = '5955e3fda040'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(op.f('organization_members_user_id_organization_id_key'), 'organization_members', ['user_id', 'organization_id'])
    op.create_table_comment(
        'organization_members',
        'Represents membership in an organization.',
        existing_comment=None,
        schema=None
    )
    op.alter_column('organizations', 's3_export_enabled',
               existing_type=sa.BOOLEAN(),
               comment='Allow exporting data to S3.',
               existing_nullable=False,
               existing_server_default=sa.text('false'))
    op.create_table_comment(
        'organizations',
        'An organization is a collection of members.',
        existing_comment=None,
        schema=None
    )
    op.create_table_comment(
        'shapes',
        'A geospatial shape.',
        existing_comment=None,
        schema=None
    )
    op.create_table_comment(
        'users',
        'Represents a user of the app.',
        existing_comment=None,
        schema=None
    )


def downgrade() -> None:
    op.drop_table_comment(
        'users',
        schema=None
    )
    op.drop_table_comment(
        'shapes',
        schema=None
    )
    op.drop_table_comment(
        'organizations',
        schema=None
    )
    op.alter_column('organizations', 's3_export_enabled', comment=None)
    op.drop_table_comment('organization_members',schema=None)
    op.drop_constraint(op.f('organization_members_user_id_organization_id_key'), 'organization_members', type_='unique')
