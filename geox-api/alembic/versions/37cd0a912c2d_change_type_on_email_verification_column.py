"""Change type on email verification column

Revision ID: 37cd0a912c2d
Revises: e7c8682a8b9d
Create Date: 2022-06-24 15:14:36.469253

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "37cd0a912c2d"
down_revision = "e7c8682a8b9d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "email_verified")
    op.add_column("users", sa.Column("email_verified", sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "users",
        "email_verified",
        existing_type=sa.Boolean(),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=True,
    )
    # ### end Alembic commands ###
