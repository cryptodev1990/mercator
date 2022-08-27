-- NOTE this is for reference, I've scrubbed secrets
-- Relied on https://docs.snowflake.com/en/user-guide/data-load-s3-config-storage-integration.html
-- Separately, uploaded a file to an s3 bucket I'd created

CREATE STORAGE INTEGRATION geox_s3_buckets
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3'
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = '<read from aws>'
  STORAGE_AWS_OBJECT_ACL = 'bucket-owner-full-control'
  STORAGE_ALLOWED_LOCATIONS = ('s3://snowflake-data-transfers/')
;

CREATE ROLE ETL_ROLE;
USE DATABASE DWH;

grant create stage on schema public to role ETL_ROLE;

grant usage on integration geox_s3_buckets to role ETL_ROLE;

use schema dwh.public;

create stage test_s3_stage
  storage_integration = geox_s3_buckets
  url = 's3://snowflake-data-transfers/ok/'
  file_format = my_csv_format;

create or replace file format my_csv_format
  type = csv
  field_delimiter = ','
  skip_header = 1
  null_if = ('NULL', 'null')
  empty_field_as_null = true;


SELECT $1, $2 FROM @test_s3_stage;
