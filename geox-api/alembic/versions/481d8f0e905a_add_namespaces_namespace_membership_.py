"""Add namespaces, namespace membership, organizations

Revision ID: 481d8f0e905a
Revises: 12711d4e23ef
Create Date: 2022-08-02 10:29:56.368726

"""
from alembic import op
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = '481d8f0e905a'
down_revision = '12711d4e23ef'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text("""
            BEGIN;
            CREATE TABLE organizations (
              id UUID PRIMARY KEY,
              admin_email VARCHAR,
              admin_user_id INTEGER REFERENCES users (id),
              name VARCHAR NOT NULL,
              created_at TIMESTAMP NOT NULL DEFAULT NOW(),
              updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
              deleted_at TIMESTAMP
            );
            CREATE TABLE namespaces (
                id INTEGER PRIMARY KEY,
                name VARCHAR NOT NULL,
                created_by_user_id INTEGER REFERENCES users (id),
                organization_id UUID REFERENCES organizations (id),
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
            CREATE TABLE namespace_members (
                id INTEGER PRIMARY KEY,
                user_id INTEGER REFERENCES users (id),
                namespace_id INTEGER REFERENCES namespaces (id),
                added_by_user_id INTEGER REFERENCES users (id),
                has_read BOOLEAN NOT NULL DEFAULT FALSE,
                has_write BOOLEAN NOT NULL DEFAULT FALSE,
                is_admin BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
                CONSTRAINT no_duplicate_user_in_namespace UNIQUE (namespace_id, user_id)
            );
            CREATE INDEX ON namespace_members(user_id);
            END;
            """)
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text("""
            BEGIN;
            DROP TABLE namespace_members;
            DROP TABLE namespaces;
            DROP TABLE organizations;
            END;
            """)
    )
