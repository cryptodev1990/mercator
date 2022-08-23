"""Add trigger to clean up orphaned organizations when a user is deleted
Add trigger to create a default user organization when a new user profile is created

Revision ID: f7cbc2d71841
Revises: a29e32a588d7
Create Date: 2022-08-06 13:06:38.640075

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7cbc2d71841'
down_revision = 'a29e32a588d7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("""
        CREATE FUNCTION remove_orphaned_organizations()
          RETURNS TRIGGER AS
          $_$
          BEGIN
            DELETE FROM organizations WHERE id NOT IN (SELECT DISTINCT organization_id FROM organization_members);
            RETURN OLD;
          END;
        $_$
        LANGUAGE 'plpgsql';

        CREATE TRIGGER users_delete_trigger
          AFTER DELETE ON "users"
            FOR EACH ROW
            EXECUTE PROCEDURE remove_orphaned_organizations();

        CREATE FUNCTION create_default_organization()
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
        LANGUAGE 'plpgsql';

        CREATE TRIGGER users_insert_trigger
          AFTER INSERT ON "users"
            FOR EACH ROW
            EXECUTE PROCEDURE create_default_organization();
        """))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("""
      DROP TRIGGER users_delete_trigger ON users;
      DROP FUNCTION remove_orphaned_organizations;
      DROP TRIGGER users_insert_trigger ON users;
      DROP FUNCTION create_default_organization;
    """))
