SELECT 1 / 0; 
-- This error is thrown intentionally, since you need to modify this script to actually get it to work
-- This script needs a bearer token to execute and you need to add that to the ellipses below

DROP FUNCTION IF EXISTS supabase_functions.send_to(email VARCHAR, subject VARCHAR, body VARCHAR);
CREATE FUNCTION supabase_functions.send_to(email VARCHAR, subject VARCHAR, body VARCHAR) 
  RETURNS INTEGER
    AS $$ SELECT net.http_post(
        url:='https://api.mercator.tech/comms/webhook'::VARCHAR,
        body:=(jsonb_build_object('to_email', email, 'subject', subject, 'body', body)),
        headers:='{"Content-Type": "application/json", "Authorization": "Bearer ..."}'::jsonb
    ) as request_id
    $$ LANGUAGE SQL;



DROP TRIGGER waitlist_insert_trigger ON waitlist;
DROP FUNCTION IF EXISTS notify_admin_on_waitlist();

CREATE OR REPLACE FUNCTION notify_admin_on_waitlist()
  RETURNS TRIGGER
  AS $_$
    DECLARE contact_id INTEGER;
    BEGIN
    SELECT supabase_functions.send_to(
      'founders@mercator.tech',
      '[automated] New mailing list sign-up',
      'New sign up: ' || NEW.email
    ) INTO contact_id;
    RETURN(NEW);
    END;
  $_$ LANGUAGE 'plpgsql';

CREATE TRIGGER waitlist_insert_trigger
    AFTER INSERT ON waitlist
    FOR EACH ROW
    EXECUTE PROCEDURE notify_admin_on_waitlist();

INSERT INTO waitlist (email) VALUES ('ajduberstein+test1@gmail.com');


DROP TRIGGER support_tickets_insert_trigger ON support_tickets;
DROP FUNCTION IF EXISTS send_support_ticket_received();
CREATE OR REPLACE FUNCTION send_support_ticket_received()
  RETURNS trigger
  AS $_$
    DECLARE contact_id INTEGER;
    BEGIN
    SELECT supabase_functions.send_to(
      NEW.email,
      '[Mercator] Feature request / bug report confirmation',
      'Hey ' || NEW.email || ',<br /><br />Thanks for the feedback -- Your issue is being reviewed. If there is a need for follow-up, expect a response in this thread.<br /><br />Best,<br />Mercator'
    ) INTO contact_id;
    SELECT supabase_functions.send_to(
      'founders@mercator.tech',
      '[automated] Feature request / bug report from ' || NEW.email,
      'Description: ' || NEW.description
    ) INTO contact_id;
    RETURN(NEW);
    END;
  $_$ LANGUAGE 'plpgsql';

CREATE TRIGGER support_tickets_insert_trigger
    AFTER INSERT ON support_tickets
    FOR EACH ROW
    EXECUTE PROCEDURE send_support_ticket_received();

-- Example
-- INSERT INTO support_tickets(email, description) VALUES ('ajduberstein+test1@gmail.com', 'This is a second test bug.');
