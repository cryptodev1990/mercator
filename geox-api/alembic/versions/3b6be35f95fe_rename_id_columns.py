"""Rename id columns

Revision ID: 3b6be35f95fe
Revises: eebacc992efa
Create Date: 2022-08-03 12:37:44.981903

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3b6be35f95fe'
down_revision = 'eebacc992efa'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        """
        BEGIN;
        ALTER TABLE db_credentials RENAME COLUMN created_by_user TO created_by_user_id;
        ALTER TABLE db_credentials RENAME COLUMN updated_by_user TO updated_by_user_id;
        END;
    """)


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        """
        BEGIN;
        ALTER TABLE db_credentials RENAME COLUMN created_by_user_id TO created_by_user;
        ALTER TABLE db_credentials RENAME COLUMN updated_by_user_id TO updated_by_user;
        END;
    """)
