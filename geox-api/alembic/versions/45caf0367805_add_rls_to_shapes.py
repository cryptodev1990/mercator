"""Add RLS to shapes

Revision ID: 45caf0367805
Revises: 1c5fdf8ce69c
Create Date: 2022-08-26 19:54:53.755497

"""
from alembic import op
import sqlalchemy as sa
from typing import Optional


# revision identifiers, used by Alembic.
revision = '45caf0367805'
down_revision = '1c5fdf8ce69c'
branch_labels = None
depends_on = None


def create_policy(name: str,
                  table_name: str,
                  to_: str = "PUBLIC",  # { role_name | PUBLIC | CURRENT_ROLE | CURRENT_USER | SESSION_USER } [, ...] ]
                  permissive: bool = True,
                  for_: str = "ALL", #  { ALL | SELECT | INSERT | UPDATE | DELETE } ]
                  using: Optional[str] = None,
                  with_check: Optional[str] = None
                  ):
    permissive_str = "PERMISSIVE" if permissive else "RESTRICTIVE"
    stmt = f"""
    CREATE POLICY {name}
    ON {table_name}
    AS {permissive_str}
    FOR {for_}
    TO {to_}
    """
    if using:
        stmt += f"USING ({using})\n"
    if with_check:
        stmt += f"WITH CHECK ({with_check})"
    return sa.text(stmt)

def create_same_org_policy(table_name, organization_id = "organization_id"):
    return create_policy("same_org", table_name,
                            to_ = "app_user",
                            for_ = "ALL",
                            using = f"app_user_org() = {organization_id}",
                            with_check = f"app_user_org() = {organization_id}")

def drop_policy(name: str, table_name: str, if_exists: bool=True):
    if_exists_str = "IF EXISTS" if if_exists else ""
    return sa.text(f"DROP POLICY {if_exists_str} {name} ON {table_name}")

def drop_same_org_policy(table_name: str, if_exists: bool=True):
    return drop_policy("same_org", table_name, if_exists=True)

def enable_rls(table_name):
    return sa.text(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY")

def disable_rls(table_name):
    return sa.text(f"ALTER TABLE {table_name} DISABLE ROW LEVEL SECURITY")

# Shapes - read

def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(enable_rls("shapes"))
    conn.execute(create_same_org_policy("shapes"))

def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(drop_same_org_policy("shapes"))
    conn.execute(disable_rls("shapes"))
