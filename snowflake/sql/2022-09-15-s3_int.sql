use role accountadmin;

-- Any time this is rerun, the externalID of the arn:aws:iam::032836561503:role/snowflake trust policy
-- needs to be reset
CREATE STORAGE INTEGRATION s3_int
    type = external_stage
    storage_provider = 'S3'
    enabled = true
    storage_aws_role_arn = 'arn:aws:iam::032836561503:role/snowflake'
    storage_allowed_locations = ('s3://mercator-geofencer-data/');

GRANT USAGE ON INTEGRATION s3_int TO ROLE sysadmin;
