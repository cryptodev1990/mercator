from alembic_utils.pg_function import PGFunction
from textwrap import dedent

__all__ = ["app_user_org"]

app_user_org = PGFunction(
  schema='public',
  signature='app_user_org()',
  definition="""
  RETURNS UUID as
  $$
    SELECT nullif(current_setting('app.user_org', TRUE), '') :: UUID;
  $$ language SQL;
  """
)
