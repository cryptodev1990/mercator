"""Add comment to organizations.s3_exports_enabled column

Revision ID: e1aadd0537a8
Revises: a7c6886c3610
Create Date: 2022-09-28 10:39:39.303464

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1aadd0537a8'
down_revision = 'a7c6886c3610'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('organizations', 's3_export_enabled',
               existing_type=sa.BOOLEAN(),
               comment='Allow exporting data to S3.',
               existing_nullable=False,
               existing_server_default=sa.text('false'))

def downgrade() -> None:
    op.alter_column('organizations', 's3_export_enabled',
               existing_type=sa.BOOLEAN(),
               comment=None,
               existing_comment='Allow exporting data to S3.',
               existing_nullable=False,
               existing_server_default=sa.text('false'))
