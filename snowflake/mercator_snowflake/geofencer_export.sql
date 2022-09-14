/* Script to setup Snowflake data sharing for an account.

Requires the organization id (in the organziations table) and
the Snowflake account id of the organization.

Jinja templated Snowflake SQL.

*/
{{ set organization_id = '5b706ffe-9608-4edd-bb00-ab9cbcb7384f' }}
{{ set account_id = 'oga02999' }}
{{ set s3_bucket = 'snowflake-data-transfers' }}
{{ set s3_path = 'geofencer/shapes' }}
{{ set db_name = 'org_' ~ (organization_id | replace("-", "") | lower) }}
{{ set share_name = 'org_' ~ (organization_id | replace("-", "") | lower) }}

-- Only accountadmin can create shares
USE ROLE accountadmin;

CREATE OR REPLACE SHARE {{share_name }};
CREATE OR REPLACE DATABASE {{ db_name }};
CREATE OR REPLACE SCHEMA {{ db_name }}.geofencer;
GRANT USAGE ON DATABASE {{ db_name }} TO SHARE {{ db_name }};
GRANT USAGE ON SCHEMA {{ db_name }}.geofencer TO SHARE {{ share_name }};
ALTER SHARE {{ db_name }} ADD ACCOUNTS = {{ account_id }};

/* Define external table and view to share with the user */

USE SCHEMA {{ db_name }}.geofencer;

CREATE OR REPLACE STAGE shapes_stage
STORAGE_INTEGRATION = geox_s3_buckets
URL = 's3://{{ s3_bucket }}/{{ s3_path }}/{{ organization_id }}/latest/';

-- Shared views can only refence objects in the same database so the external table
-- must be in the org database
CREATE OR REPLACE EXTERNAL TABLE shapes_external
(
    created_by_user_id NUMBER(38, 0) AS ($1:created_by_user_id::NUMBER(38, 0)),
    name TEXT AS ($1:name::TEXT),
    geojson OBJECT AS (parse_json($1:geojson::TEXT)::OBJECT),
    created_at TIMESTAMP_NTZ AS ($1:created_at::TIMESTAMP_NTZ),
    updated_at TIMESTAMP_NTZ AS ($1:updated_at::TIMESTAMP_NTZ),
    exported_at TIMESTAMP_NTZ AS ($1:exported_at::TIMESTAMP_NTZ),
    uuid TEXT AS ($1:uuid::TEXT)
)
LOCATION = @shapes_stage
REFRESH_ON_CREATE = True
AUTO_REFRESH = True
FILE_FORMAT = shared.mercator.geofencer_shapes_format;

CREATE OR REPLACE SECURE VIEW shapes
AS
SELECT
    uuid,
    geojson
    name,
    created_at,
    updated_at,
    exported_at
FROM shapes_external;

GRANT SELECT ON VIEW shapes TO SHARE {{ db_name }};
