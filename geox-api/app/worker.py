"""Celery worker."""
from functools import lru_cache
from typing import Any, Dict, Optional, cast
from uuid import UUID, uuid4

import geopandas as gpd
import s3fs
from celery.utils.log import get_task_logger
from sqlalchemy import create_engine, text

from app.core.celery_app import celery_app
from app.core.config import get_settings
from app.core.datatypes import AppEnvEnum

_settings = get_settings()

logger = get_task_logger(__name__)


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    """Dummy task to return a work in a Celery worker."""
    return f"test task return {word}"


# Workers will run in a seperate processes than main app
# these use seperate connection settings than the main app
# in order to allow the main app settings to propogate through
# dependencies. If this used the globals in app/db/ then there is
# no way to overwrite changes in settings via Depends() in the
# routes.


@lru_cache(maxsize=1)
def get_postgres_engine():
    postgres_connection_url = _settings.sqlalchemy_database_uri
    opts = _settings.worker_engine_opts.dict()
    return create_engine(postgres_connection_url, pool_pre_ping=True, future=True, **opts)


def send_data_to_s3(
    df: gpd.GeoDataFrame,
    organization_id: str,
    aws_s3_url: str,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    app_env: AppEnvEnum = AppEnvEnum.dev,
) -> str:
    """Send data to S3.

    Returns:
        Output path in S3 of the files written.
    """
    # if app-env is development the organization_id is ignored in the S3
    # output path ignored and result goes to a fake UUID path on S3.
    if app_env == AppEnvEnum.dev:
        organization_id = str(UUID(int=0))
    rnd = str(uuid4())[:6]
    now = df["exported_at"][0]
    export_id = (
        f"{now.year}/{now.month:02d}/{now.day:02d}/{now.hour:02d}/{now.minute:02d}/"
        f"{now.second:02d}/{now.microsecond:06d}/{rnd}"
    )
    df["export_id"] = export_id
    path = (
        f"{aws_s3_url}export/shapes/{organization_id}/{export_id}/data.parquet"
    ).replace("s3://", "")
    fs = s3fs.S3FileSystem(key=aws_access_key_id, secret=aws_secret_access_key)
    # fs.open() does not need the S3 protocol so remove it from the path
    with fs.open(path, "wb") as f:
        df.to_parquet(
            f,
            index=False,
            compression="snappy",
            engine="pyarrow",
        )
    return path


def query_shapes_table(
    organization_id: str,
) -> gpd.GeoDataFrame:
    engine = get_postgres_engine()
    with engine.begin() as conn:
        logger.debug(f"Copy shapes for {organization_id}")
        # TODO: save as geoparquet with geopandas
        query = text(
            """
                SELECT
                    uuid :: TEXT AS uuid,
                    name,
                    -- WKB Format in WG84 projection
                    geom,
                    -- to avoid certain issues writing to parquet like
                    -- ArrowNotImplementedError: Cannot write struct type 'properties' with no child field to Parquet. Consider adding a dummy child field.
                    properties - '__uuid' - 'name' AS properties,
                    -- ensure that there is no timezone
                    created_at::TIMESTAMP AS created_at,
                    updated_at::TIMESTAMP AS updated_at,
                    deleted_at::TIMESTAMP AS deleted_at,
                    (now() at time zone 'utc')::TIMESTAMP AS exported_at,
                    organization_id :: TEXT AS organization_id
                FROM shapes
                WHERE 1=1
                    AND organization_id = :organization_id
                ORDER BY created_at
                """
        )
        df = gpd.read_postgis(
            query, conn, geom_col="geom", params={"organization_id": organization_id}
        )
        return cast(gpd.GeoDataFrame, df)


@celery_app.task(acks_late=True)
def copy_to_s3(
    organization_id: str,
    aws_s3_url: str,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Copy data from postgres shapes into S3.

    This task does two things:

    1. Export shapes from the organization in the App to S3
    2. Copy shapes from S3 into Snowflake

    Args:
        organization_id: Organization ID - only shapes from that organization are extracted.
        app_db_connection_url: Connection URL for the app database. The workers run in a seperate processes
            so don't reuse the same engine as the app itself.
        aws_s3_url: S3 url where shape files will go(``s3://bucket-name/path/to/place/files/``)
        aws_access_key_id:. AWS access key to be able to write to ``aws_s3_url``.
        aws_secret_access_key (Optional[str], optional): AWS access key to be able to write to ``aws_s3_url``.
    Returns:
        Dict[str, Any]: A dictionary with the number of shapes written.
    """
    df = query_shapes_table(organization_id)
    # NOTE: Exiting if no shapes are exported means that if there were shapes exported,
    # and the user deleted all shapes, then those shapes would not be deleted. Is this the
    # desired behavior? Not sure.
    num_rows = df.shape[0]
    if num_rows:
        output_path = send_data_to_s3(
            df,
            organization_id,
            aws_s3_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        logger.debug("Exported data to %s", output_path)
    else:
        logger.debug("No results, not exporting shapes to S3.")
    return {
        "num_rows": num_rows,
    }
