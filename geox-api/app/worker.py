"""Celery worker."""
import csv
import json
from typing import Optional

import awswrangler as wr
import boto3
import pandas as pd
from celery.utils.log import get_task_logger
from pydantic import UUID4
from sqlalchemy import text

from app.core.celery_app import celery_app
from app.core.config import get_settings
from app.db.session import SessionLocal

logger = get_task_logger(__name__)


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    """Dummy task to return a work in a Celery worker."""
    return f"test task return {word}"


settings = get_settings()


def send_data_to_s3(df: pd.DataFrame, org_id: UUID4):

    aws_secret_access_key: Optional[str]
    if settings.aws_s3_upload_secret_access_key:
        aws_secret_access_key = (
            settings.aws_s3_upload_secret_access_key.get_secret_value()
        )
    else:
        aws_secret_access_key = None

    # Boto3 session
    session = boto3.Session(
        aws_access_key_id=settings.aws_s3_upload_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    res = wr.s3.to_csv(
        df,
        path=f"s3://snowflake-data-transfers/shapes/{org_id}-latest.csv.gz",
        sep="\x01",
        index=False,
        quoting=csv.QUOTE_NONE,
        compression="gzip",
        boto3_session=session,
    )

    return res


@celery_app.task(acks_late=True)
def copy_to_s3(organization_id: UUID4) -> dict:
    """Copy data from postgres shapes to S3.

    TODO ideally this gets replaced by FiveTran
    Currently, on Fly.io, I can't connect directly to FiveTran.

    Returns number of rows copied.
    """
    db = SessionLocal()
    print(f"Executing for organization {organization_id}")
    logger.info(f"Executing for organization {organization_id}")
    shapes = db.execute(
        text(
            """
        SELECT uuid
        , name
        , created_at
        , updated_at
        , geojson
        FROM shapes
        WHERE 1=1
          AND (
            created_by_user_id IN (
              SELECT user_id
              FROM organization_members
              WHERE organization_id = :organization_id
            ) OR updated_by_user_id IN (
              SELECT user_id
              FROM organization_members
              WHERE organization_id = :organization_id
            )
          )
          AND deleted_at IS NULL
        ORDER BY created_at
    """
        ),
        {"organization_id": organization_id},
    )
    print(f"{shapes.rowcount} shapes found")
    if shapes.rowcount == 0:
        raise Exception("No shapes to publish")
    df = pd.DataFrame(shapes.fetchall())
    df.uuid = df.uuid.astype(str)
    df["geojson"] = df.geojson.map(lambda x: json.dumps(x))
    res = send_data_to_s3(df, organization_id)
    logger.info(res)
    return {"num_rows": len(df)}
