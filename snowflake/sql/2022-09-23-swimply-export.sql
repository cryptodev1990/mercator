/* Adding soft delete - Migrating the one existing org export, swimply */
ALTER TABLE ORG_B02FE057DE0540A0B04A7742A1189B91.geofencer.shapes_exports ADD COLUMN deleted_at TIMESTAMP_NTZ(9);
COMMENT ON COLUMN ORG_B02FE057DE0540A0B04A7742A1189B91.geofencer.shapes_exports.deleted_at IS 'Deleted at time. If not `NULL`, then this shape has been deleted.';

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
        st_geographyfromwkb($1:geom::BINARY),
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

CREATE OR REPLACE SECURE VIEW ORG_B02FE057DE0540A0B04A7742A1189B91.geofencer.shapes
AS
SELECT
    uuid,
    name,
    geom,
    properties,
    updated_at,
    exported_at
FROM ORG_B02FE057DE0540A0B04A7742A1189B91.geofencer.shapes_exports
WHERE export_id = (SELECT max(export_id) FROM ORG_B02FE057DE0540A0B04A7742A1189B91.geofencer.shapes_exports)
    AND deleted_at IS NULL;

COMMENT ON VIEW ORG_B02FE057DE0540A0B04A7742A1189B91.geofencer.shapes IS $$Latest Geofencer shapes.$$;

GRANT SELECT ON VIEW ORG_B02FE057DE0540A0B04A7742A1189B91.geofencer.shapes TO SHARE ORG_B02FE057DE0540A0B04A7742A1189B91_SHARE;

CREATE OR REPLACE SECURE VIEW ORG_B02FE057DE0540A0B04A7742A1189B91.geofencer.shapes_latest_with_deleted
AS
SELECT
    uuid,
    name,
    geom,
    properties,
    updated_at,
    deleted_at,
    exported_at
FROM ORG_B02FE057DE0540A0B04A7742A1189B91.geofencer.shapes_exports
WHERE export_id = (SELECT max(export_id) FROM ORG_B02FE057DE0540A0B04A7742A1189B91.geofencer.shapes_exports);

COMMENT ON VIEW ORG_B02FE057DE0540A0B04A7742A1189B91.geofencer.shapes_latest_with_deleted IS $$Latest export of Geofencer shapes, including deleted shapes.$$;

GRANT SELECT ON VIEW ORG_B02FE057DE0540A0B04A7742A1189B91.geofencer.shapes_latest_with_deleted TO SHARE ORG_B02FE057DE0540A0B04A7742A1189B91_SHARE;

desc share ORG_B02FE057DE0540A0B04A7742A1189B91_SHARE;

