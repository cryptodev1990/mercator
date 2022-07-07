"""Update shapes table

Revision ID: 7e39c76ae11e
Revises: 0fb1541954de
Create Date: 2022-07-07 13:44:27.008763

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7e39c76ae11e'
down_revision = '0fb1541954de'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('shapes', 'geojson',
               existing_type=postgresql.JSONB(astext_type=sa.Text()),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('shapes', 'geojson',
               existing_type=postgresql.JSONB(astext_type=sa.Text()),
               nullable=True)
    # ### end Alembic commands ###
