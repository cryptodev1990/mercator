/* Setup Integration to send Snowpipe errors to SNS

See https://docs.snowflake.com/en/user-guide/data-load-snowpipe-errors-sns.html

*/

USE ROLE accountadmin;
CREATE NOTIFICATION INTEGRATION snowpipe_sns_int
  ENABLED = true
  TYPE = QUEUE
  NOTIFICATION_PROVIDER = AWS_SNS
  DIRECTION = OUTBOUND
  AWS_SNS_TOPIC_ARN = 'arn:aws:sns:us-east-2:032836561503:snowflake_snowpipe'
  AWS_SNS_ROLE_ARN = 'arn:aws:iam::032836561503:role/snowflake';

-- Values of SF_AWS_IAM_USER_ARN and SF_AWS_EXTERNAL_ID needed for
-- external trust policy of arn:aws:iam::032836561503:role/snowflake
-- see https://docs.snowflake.com/en/user-guide/data-load-snowpipe-errors-sns.html
DESC NOTIFICATION INTEGRATION snowpipe_sns_int;

GRANT USAGE ON INTEGRATION snowpipe_sns_int TO ROLE geofencer_etl_role;

/*
Migrate existing accounts
*/

USE role geofencer_etl_role;
ALTER PIPE org_b02fe057de0540a0b04a7742a1189b91.geofencer.shapes_pipe SET ERROR_INTEGRATION = snowpipe_sns_int;
ALTER PIPE org_E6CEF492506946D38431FDA523CAF2F6.geofencer.shapes_pipe SET ERROR_INTEGRATION = snowpipe_sns_int;
