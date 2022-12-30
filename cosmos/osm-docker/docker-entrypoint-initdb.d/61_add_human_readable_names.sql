BEGIN;

-- copy CSV of OpenAI-generated human readable names into database
CREATE TEMPORARY TABLE osm_human_readable_categories (
  slug VARCHAR,
  human_readable VARCHAR
);

CREATE INDEX ON osm_human_readable_categories(slug);
-- TODO how do we automate this copy?
SELECT 'NOTE copy the file cleaned_categories.dsv before running this script or it will fail' AS message;
\copy osm_human_readable_categories FROM '/tmp/cleaned_categories.dsv' DELIMITER '|' CSV HEADER;

CREATE TEMPORARY TABLE category_membership_swap AS
  SELECT osm_id
  , category
  , human_readable
  FROM category_membership
  JOIN osm_human_readable_categories
  ON slug = category
;

-- promote
DROP TABLE category_membership;
CREATE TABLE category_membership AS
SELECT *
FROM category_membership_swap;

-- Support fast ILIKE/LIKE queries on these categories
CREATE INDEX CONCURRENTLY category_trgm ON category_membership USING gin (human_readable gin_trgm_ops);

END;
