/* Fix Swimply account - don't fail if one shape is bad */

-- Replace pipe to read in deleted at
CREATE OR REPLACE PIPE ORG_B02FE057DE0540A0B04A7742A1189B91.geofencer.shapes_pipe
AUTO_INGEST=TRUE
AS
COPY INTO ORG_B02FE057DE0540A0B04A7742A1189B91.geofencer.shapes_exports
(uuid, name, geom, properties, created_at, updated_at, deleted_at, exported_at, organization_id, export_id)
FROM (
    SELECT
        $1:uuid::TEXT,
        $1:name::TEXT,
        -- geo is stored in wkb format
        try_to_geography($1:geom::BINARY),
        coalesce(parse_json($1:properties::TEXT)::OBJECT, object_construct()),
        -- this seems to work for reading timestamps from parquet.
        -- the scale is important - the wrong scale
        to_timestamp_ntz($1:created_at::INT, 6),
        to_timestamp_ntz($1:updated_at::INT, 6),
        to_timestamp_ntz($1:deleted_at::INT, 6),
        to_timestamp_ntz($1:exported_at::INT, 6),
        $1:organization_id::TEXT,
        $1:export_id::TEXT
    FROM @ORG_B02FE057DE0540A0B04A7742A1189B91.geofencer.shapes_stage
)
FILE_FORMAT=(TYPE=parquet COMPRESSION=snappy BINARY_AS_TEXT=false);
