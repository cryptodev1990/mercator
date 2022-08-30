CREATE DATABASE shared;
USE DATABASE shared;

CREATE SCHEMA mercator;
USE SCHEMA mercator;

CREATE OR REPLACE FILE FORMAT shape_csv_format
  TYPE = CSV
  FIELD_DELIMITER = '\x01'
  SKIP_HEADER = 1
  NULL_IF = ('NULL', 'null')
  EMPTY_FIELD_AS_NULL = TRUE
;

CREATE STAGE duberstein_shapes_s3_stage
  STORAGE_INTEGRATION = geox_s3_buckets
  URL = 's3://snowflake-data-transfers/shapes-d702f23c-c44c-4833-9d84-81642af87906-latest.csv'
  FILE_FORMAT = shape_csv_format
;

-- DEMO SHARE
CREATE OR REPLACE TABLE duberstein_shapes AS
SELECT $1 AS uuid 
, $2 AS name
, $3 AS created_at
, $4 AS updated_at
, $5 AS geojson
FROM @duberstein_shapes_s3_stage;

CREATE SHARE duberstein_share;
GRANT USAGE ON DATABASE shared TO SHARE duberstein_share;
grant select on table duberstein_shapes to share duberstein_share;
