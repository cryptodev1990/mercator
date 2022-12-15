import psycopg2

from app.core.config import get_settings

settings = get_settings()

conn = psycopg2.connect(
    host=settings.db.server,
    port=settings.db.port,
    database=settings.db.database,
    user=settings.db.user,
    password=settings.db.password
)