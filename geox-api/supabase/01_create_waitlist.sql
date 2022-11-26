DROP TABLE IF EXISTS waitlist;
CREATE TABLE IF NOT EXISTS waitlist (
  id SERIAL PRIMARY KEY ,
  email VARCHAR NOT NULL UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  contacted_at TIMESTAMP
);
ALTER TABLE waitlist ENABLE ROW LEVEL SECURITY;

CREATE POLICY "No read for anon user"
  ON waitlist FOR SELECT
  TO anon
USING (
  FALSE
)
;

DROP POLICY "No update for anon user" ON waitlist;
CREATE POLICY "No update for anon user"
ON waitlist FOR UPDATE
TO anon
USING (
  FALSE
)
;

CREATE POLICY "No delete for anon user"
ON waitlist FOR DELETE
TO anon
USING (
  FALSE
)
;

DROP POLICY "All users can insert" ON waitlist;
CREATE POLICY "All users can insert"
ON waitlist FOR INSERT
WITH CHECK (TRUE)
;

-- select * from pg_policies;
