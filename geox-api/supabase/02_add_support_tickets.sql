DROP TABLE IF EXISTS support_tickets;
CREATE TABLE IF NOT EXISTS support_tickets (
  id SERIAL PRIMARY KEY,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  description VARCHAR NOT NULL,
  email VARCHAR NOT NULL,
  screenshot_path VARCHAR,
  addressed BOOLEAN
);
ALTER TABLE support_tickets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "No read for anon user"
  ON support_tickets FOR SELECT
  TO anon
USING (
  FALSE
)
;

DROP POLICY "No update for anon user" ON support_tickets;
CREATE POLICY "No update for anon user"
ON support_tickets FOR UPDATE
TO anon
USING (
  FALSE
)
;

CREATE POLICY "No delete for anon user"
ON support_tickets FOR DELETE
TO anon
USING (
  FALSE
)
;

DROP POLICY "All users can insert" ON support_tickets;
CREATE POLICY "All users can insert"
ON support_tickets FOR INSERT
WITH CHECK (TRUE)
;

-- select * from pg_policies;
