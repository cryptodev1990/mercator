"""Enable RLS on namespaces

Revision ID: 971512274734
Revises: ffe9aec65323
Create Date: 2022-10-12 15:39:09.505534

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "971512274734"
down_revision = "ffe9aec65323"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("ALTER TABLE namespaces ENABLE ROW LEVEL SECURITY"))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("ALTER TABLE namespaces DISABLE ROW LEVEL SECURITY"))
