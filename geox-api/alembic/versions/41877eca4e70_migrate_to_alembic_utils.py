"""Migrate to alembic_utils

Revision ID: 41877eca4e70
Revises: 710a857ba43b
Create Date: 2022-10-05 17:31:28.506652

No changes when migrating to managing extensions, policies,

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '41877eca4e70'
down_revision = '710a857ba43b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table_comment(
        'shapes',
        existing_comment='A geospatial shape.',
        schema=None
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table_comment(
        'shapes',
        'A geospatial shape.',
        existing_comment=None,
        schema=None
    )
    # ### end Alembic commands ###
