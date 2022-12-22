-- Create indexes on tables
CREATE INDEX ON osm (osm_type);

-- indexes only the existence of tags
CREATE INDEX ON osm USING GIN (tags);

-- Full txt search table
ALTER TABLE osm

ADD COLUMN fts tsvector GENERATED ALWAYS AS (TO_TSVECTOR('english', tags)) STORED;
CREATE INDEX ON osm USING GIN (fts);
