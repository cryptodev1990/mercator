"""Remove membership mixins

Revision ID: 7f6fb9c3c570
Revises: 65933c2941c3
Create Date: 2022-08-30 14:26:27.951665

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f6fb9c3c570'
down_revision = '65933c2941c3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("""
        CREATE OR REPLACE FUNCTION create_default_organization()
          RETURNS trigger AS
          $_$
          DECLARE
            new_organization_id UUID;
          BEGIN
            INSERT INTO organizations (name, created_at, updated_at, is_personal) VALUES
              (
                COALESCE(NEW."nickname" || ' Workspace', NEW.email || ' - Default Workspace'),
                NOW(),
                NOW(),
                TRUE
              ) RETURNING id INTO new_organization_id;
            INSERT INTO organization_members (organization_id, user_id, created_at, updated_at, active) VALUES (new_organization_id, NEW."id", NOW(), NOW(), TRUE);
            RETURN NEW;
          END;
        $_$
        LANGUAGE 'plpgsql';
    """))
    op.drop_column('organization_members', 'has_read')
    op.drop_column('organization_members', 'has_write')
    op.drop_column('organization_members', 'is_admin')

def downgrade() -> None:
    conn = op.get_bind()
    op.add_column('organization_members', sa.Column('is_admin', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('organization_members', sa.Column('has_write', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('organization_members', sa.Column('has_read', sa.BOOLEAN(), autoincrement=False, nullable=False))
    conn.execute(sa.text("""
        CREATE OR REPLACE FUNCTION create_default_organization()
          RETURNS trigger AS
          $_$
          DECLARE
            new_organization_id UUID;
          BEGIN
            INSERT INTO organizations (name, created_at, updated_at) VALUES
              (
                COALESCE(NEW."nickname" || ' Workspace', NEW.email || ' - Default Workspace'),
                NOW(),
                NOW()
              ) RETURNING id INTO new_organization_id;
            INSERT INTO organization_members (organization_id, created_at, updated_at, user_id, has_write, has_read, is_admin) VALUES (new_organization_id, NOW(), NOW(), NEW."id", TRUE, TRUE, TRUE);
            RETURN NEW;
          END;
        $_$
        LANGUAGE 'plpgsql';"""))