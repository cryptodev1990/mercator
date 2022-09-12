SELECT email
, id
FROM users
;
-- duber@mercator.tech is user id = 1
-- jeffrey.arnold@gmail is user id = 3

INSERT INTO organizations (name, is_personal, created_at, updated_at) VALUES (
  'Mercator', false, NOW(), NOW()
);


-- Mercator ORG ID is e6cef492-5069-46d3-8431-fda523caf2f6

BEGIN;
  INSERT INTO organization_members (user_id, organization_id, created_at, active, updated_at) VALUES
    (1, 'e6cef492-5069-46d3-8431-fda523caf2f6', NOW(), true, NOW()),
    (3, 'e6cef492-5069-46d3-8431-fda523caf2f6', NOW(), true, NOW())
  ;
  UPDATE organization_members SET active = False
    WHERE 1=1
      AND user_id IN (1, 3)
      AND organization_id != 'e6cef492-5069-46d3-8431-fda523caf2f6'
  ;
END;


BEGIN;
  INSERT INTO organization_members (user_id, organization_id,
	created_at, active, updated_at) VALUES
    (4, 'e6cef492-5069-46d3-8431-fda523caf2f6', NOW(), true, NOW())
  ;
  UPDATE organization_members SET active = False
    WHERE 1=1
      AND user_id IN (4)
      AND organization_id != 'e6cef492-5069-46d3-8431-fda523caf2f6'
  ;
END;


BEGIN;
  UPDATE organization_members SET active = True WHERE organization_id != 'e6cef492-5069-46d3-8431-fda523caf2f6' AND user_id = 3;
  UPDATE organization_members SET active = False WHERE organization_id = 'e6cef492-5069-46d3-8431-fda523caf2f6' AND user_id = 3;
END;
