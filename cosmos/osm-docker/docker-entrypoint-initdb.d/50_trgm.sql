CREATE EXTENSION pg_trgm;
ALTER TABLE osm ADD COLUMN tags_text TEXT;
UPDATE osm SET tags_text = cast(tags AS TEXT);
CREATE INDEX osm_tags_text_trgm_idx ON osm USING GIST (tags_text gist_trgm_ops);
