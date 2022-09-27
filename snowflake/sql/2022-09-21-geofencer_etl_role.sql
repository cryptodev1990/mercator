/* Role to use for creating geofencer ETLs and Sharing */
USE ROLE accountadmin;
CREATE ROLE geofencer_etl_role;
-- create a new database for each org
GRANT CREATE DATABASE ON ACCOUNT TO ROLE geofencer_etl_role;
-- Be able to read S3 integrations
GRANT USAGE ON INTEGRATION s3_int TO ROLE geofencer_etl_role;
-- Share data to organizations
GRANT CREATE SHARE ON ACCOUNT TO ROLE geofencer_etl_role;
