"""Add db credentials table

Revision ID: e6eebb335f5f
Revises: 481d8f0e905a
Create Date: 2022-08-02 15:14:54.563245

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'e6eebb335f5f'
down_revision = '481d8f0e905a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        """
            CREATE TABLE db_credentials (
              id UUID PRIMARY KEY,
              name VARCHAR NOT NULL,
              organization_id UUID REFERENCES organizations(id),
              is_default BOOLEAN NOT NULL DEFAULT FALSE,
              created_at TIMESTAMP NOT NULL DEFAULT NOW(),
              created_by_user INTEGER REFERENCES users(id),
              updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
              updated_by_user INTEGER REFERENCES users(id),
              db_driver VARCHAR NOT NULL,
              db_user VARCHAR NOT NULL,
              db_password VARCHAR NOT NULL,
              db_host VARCHAR NOT NULL,
              db_port VARCHAR NOT NULL,
              db_database VARCHAR NOT NULL,
              db_extras VARCHAR NOT NULL
            );
            """)


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute("""DROP TABLE db_credentials;""")
