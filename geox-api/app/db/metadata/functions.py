from alembic_utils.pg_function import PGFunction
from alembic_utils.replaceable_entity import register_entities

entities = []
"""List of objects to monitor"""

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

entities.append(app_user_org)
