"""Add organization column to users and namespace column to shapes

Revision ID: eebacc992efa
Revises: e6eebb335f5f
Create Date: 2022-08-02 17:06:47.409212

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'eebacc992efa'
down_revision = 'e6eebb335f5f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        """ALTER TABLE users ADD COLUMN organization_id UUID REFERENCES organizations(id);""")
    conn.execute(
        """ALTER TABLE shapes ADD COLUMN namespace_id INTEGER REFERENCES namespaces(id);""")


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        """ALTER TABLE users DROP COLUMN organization_id;""")
    conn.execute(
        """ALTER TABLE shapes DROP COLUMN namespace_id;""")