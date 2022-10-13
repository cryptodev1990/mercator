/*
Create an S3 integration for development.

*/
use role accountadmin;

-- Any time this is rerun, the externalID of the arn:aws:iam::032836561503:role/snowflake trust policy
-- needs to be reset
CREATE STORAGE INTEGRATION s3_int_dev
    type = external_stage
    storage_provider = 'S3'
    enabled = true
    storage_aws_role_arn = 'arn:aws:iam::032836561503:role/snowflake'
    storage_allowed_locations = ('s3://mercator-geofencer-data-dev/');

DESC STORAGE INTEGRATION s3_int_dev;
// Update trust policy of arn:aws:iam::032836561503:role/snowflake with values from this
/*
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "{{ STORAGE_AWS_IAM_USER_ARN }}"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {
                    "sts:ExternalId": "{{STORAGE_AWS_EXTERNAL_ID}}"
                }
            }
        }
*/
GRANT USAGE ON INTEGRATION s3_int_dev TO ROLE sysadmin;
GRANT usage ON integration s3_int_dev TO ROLE geofencer_etl_role;
