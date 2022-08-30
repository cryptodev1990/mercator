-- Relied on https://docs.snowflake.com/en/user-guide/data-load-s3-config-storage-integration.html
-- Separately, uploaded a file to an s3 bucket I'd created

USE ROLE accountadmin;
SELECT system$get_snowflake_platform_info();

CREATE STORAGE INTEGRATION geox_s3_buckets
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3'
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::032836561503:role/mysnowflakerole'  -- Associated with our AWS account
  STORAGE_AWS_OBJECT_ACL = 'bucket-owner-full-control'
  STORAGE_ALLOWED_LOCATIONS = ('s3://snowflake-data-transfers/')
;
