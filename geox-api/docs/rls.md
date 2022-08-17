# Row Level Security

## Overview

Multi-tenancy is implemented using Postgres [Row Level Security](PostgreSQL_ Documentation_ 14_ 5.8. Row Security Policies) (RLS).

The current user is identified using the value of the `app.user_id` setting.

The value of `app.user_id = ''` when outside of a transaction in a request,
and `app.user_id` is set to the user id inside of transactions.

## Implementation

### Database Sessions

To user a session that correctly sets `app.user_id` inside of transactions, add `app.dependencies.get_app_user_session` as a [dependency](https://fastapi.tiangolo.com/tutorial/dependencies/) to route functions.

- Check for the existence of HTTP authentication with a bearer token
- Check the validity of the JWT
- Create or update a user in the app database using the JWT data
- Create a database session where the setting `app.user_id` is set to the value of the authorized
  user within each transaction.

The function `get_app_user_session` returns a `UserSession` object which contains two properties:
`session`, a Session object, and `user`, a `schemas.User` object.

```python
from app.dependencies import get_app_user_session

@app.get("/something")
def path_function(..., user_session = Depends(get_app_user_session)):
    db_session = user_session.session  # Session object
    user = user_session.user # schemas.User object
    with db_session.begin():  # implicit BEGIN
        # implicit SET LOCAL app.user_id = user_id;
        db_session.execute("SELECT 1")  # code that uses session
    # implicit COMMIT
```

### Postgres Settings

Settings can be set for the session or transaction.

- `SET SESSION app.user_id = '1'` or equivalently, `SET app.user_id = '1'`: Valid for the session (connection).
- `SET LOCAL app.user_id = '1'`: Valid for the transaction

Example:

```sql
SET app.user_id = '1';
SELECT current_setting('app.user_id');
-- 1
BEGIN;
SELECT current_setting('app.user_id');
-- 1
SET LOCAL app.user_id = '2'
SELECT current_setting('app.user_id');
-- 2
COMMIT;
SELECT current_setting('app.user_id');
-- 1
```

Notes:

- If the setting is not set then `SELECT current_setting('app.user_id')` raises an error. The
  setting should be set like `SET app.user_id TO DEFAULT` on connection creation.
- The use of `app.*` is something of a a hack. Postgres settings must be specified in a conf file, but
  it allows arbitrary settings if they include a `.`.

Implications of local and session settings with SQLALchemy:

- Since SQLAlchemy sessions are not guaranteed to use the same connection, using `SET SESSION app.user_id`
  could leak the setting across the users.
- Using `SET LOCAL app.user_id` is safer. It relies on Postgres to isolate the setting change within the
  transaction. SQLAlchemy session will use the same connection within a transaction. However, this requires
  calling the `SET LOCAL app.user_id` at the start of each new transaction. A listener on the [after_begin](https://docs.sqlalchemy.org/en/14/orm/events.html#sqlalchemy.orm.SessionEvents.after_begin) event can be used to add that code.

The value of `app.user_id` is set to the default value, `''`, when a connection is created,
checked out of the pool, or checked into the pool.

```sql
SET app.user_id TO DEFAULT;
```

For each transaction in a session within request, the value of the `app.user_id` settings is set to the user id.

```sql
BEGIN;
SET LOCAL app.user_id = ?;
-- other code
COMMIT;
```

In this app, these SQL statements are called using [SQLAlchemy events](https://docs.sqlalchemy.org/en/14/core/event.html) on
the "connect", "checkin", and "checkout" events of the `app.db.sessions.engine`, and the "after_begin" event of session instances created by `app.dependencies.get_app_user_session`.

## References

- https://aws.amazon.com/blogs/database/multi-tenant-data-isolation-with-postgresql-row-level-security/
- https://supabase.com/docs/guides/auth/row-level-security