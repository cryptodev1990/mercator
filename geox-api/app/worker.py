"""Celery worker."""
from app.core.celery_app import celery_app
from pydantic import UUID4
from sqlalchemy import text


from app.db.session import SessionLocal



@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    """Dummy task to return a work in a Celery worker."""
    return f"test task return {word}"


@celery_app.task()
def copy_to_s3(organization_id: UUID4) -> bool:
    """Copy data from postgres shapes to S3.
    
    TODO ideally this gets replaced by FiveTran
    Currently, on Fly.io, I can't connect directly to FiveTran.
    """
    db = SessionLocal()
    shapes = db.execute(text("""
        SELECT uuid
        , name
        , created_at
        , updated_at
        , geojson
        FROM shapes
        WHERE 1=1
          AND organization_id = :organization_id
          AND deleted_at IS NULL
        ORDER BY created_at
    """), {"organization_id": organization_id})
    return True