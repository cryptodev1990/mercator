from alembic_utils.pg_function import PGFunction
from textwrap import dedent

__all__ = ["app_user_id"]

app_user_id = PGFunction(
  schema='public',
  signature='app_user_id()',
  definition=dedent("""
    RETURNS integer
    LANGUAGE sql
    SECURITY DEFINER
    AS
    $function$
        SELECT nullif(current_setting('app.user_id', TRUE), '')::INTEGER
    $function$
    """))
