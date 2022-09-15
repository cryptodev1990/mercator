"""Celery worker."""
import datetime
import json
from typing import Any, Dict, Optional

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

settings = get_settings()


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    """Dummy task to return a work in a Celery worker."""
    return f"test task return {word}"


def send_data_to_s3(df: pd.DataFrame, organization_id: UUID4):
    df["uuid"] = df.uuid.astype(str)
    df["geojson"] = df.geojson.map(lambda x: json.dumps(x))
    df["exported_at"] = datetime.datetime.utcnow()

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
    aws_s3_uri = settings.aws_s3_uri
    path: str = f"s3://{aws_s3_uri}export/shapes/{organization_id}/latest/data.parquet"
    res = wr.s3.to_parquet(
        df,
        path=path,
        index=False,
        boto3_session=session,
        compression="snappy",
    )
    return res


@celery_app.task(acks_late=True)
def copy_to_s3(organization_id: UUID4) -> Dict[str, Any]:
    """Copy data from postgres shapes to S3.

    Returns number of rows copied.
    """
    with SessionLocal() as db:
        logger.debug(f"Copy shapes for {organization_id}")
        shapes = db.execute(
            text(
                """
                    SELECT uuid
                    , name
                    , geojson
                    , created_at
                    , updated_at
                    FROM shapes
                    WHERE 1=1
                        AND deleted_at IS NULL
                        AND organization_id = :organization_id
                    ORDER BY created_at
                """
            ),
            {"organization_id": organization_id},
        )
        # The organization id is redundant
        logger.debug(f"{shapes.rowcount} shapes found")
        if shapes.rowcount == 0:
            num_rows = 0
        else:
            df = pd.DataFrame(shapes.fetchall())
            send_data_to_s3(df, organization_id)
            num_rows = df.shape[0]
        return {"num_rows": num_rows}
