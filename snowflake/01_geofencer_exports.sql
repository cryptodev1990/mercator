
/* Create database used to share geofencer data via Snowflake */
USE ROLE sysadmin;

CREATE OR REPLACE DATABASE geofencer;
CREATE OR REPLACE SCHEMA geofencer.exports;

CREATE OR REPLACE STAGE geofencer.exports.shapes_stage
STORAGE_INTEGRATION = s3_int
URL = 's3://mercator-geofencer-data/export/shapes/'
COMMENT = 'Output location of exported geofencer shapes';

CREATE OR REPLACE FILE FORMAT geofencer.exports.shapes_format
TYPE = parquet
COMPRESSION = snappy
COMMENT = 'File format of exported geofencer shapes';
