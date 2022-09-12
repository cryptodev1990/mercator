-- I ran the SQL here to get our two Swimply users in the same
-- organization.
-- Ran around 10:55am Pacific on Monday Sep 12 2022

-- Pulled user IDs here
SELECT id
FROM users
WHERE 1=1
  AND email LIKE '%@swimply.com'
;


INSERT INTO organizations (name, is_personal, created_at, updated_at) VALUES (
  'Swimply', false, NOW(), NOW()
);

SELECT * FROM organizations WHERE name = 'Swimply';

BEGIN;
  INSERT INTO organization_members (user_id, organization_id, created_at, active, updated_at) VALUES
    (7, 'b02fe057-de05-40a0-b04a-7742a1189b91', NOW(), true, NOW()),
    (8, 'b02fe057-de05-40a0-b04a-7742a1189b91', NOW(), true, NOW())
  ;
  UPDATE organization_members SET active = False
    WHERE 1=1
      AND user_id IN (SELECT id
       FROM users
       WHERE 1=1
         AND email LIKE '%@swimply.com')
      AND organization_id != 'b02fe057-de05-40a0-b04a-7742a1189b91'
  ;
END;

-- Verify current organization enrollment
SELECT o.name AS organization_name
, u.email
, u.name
FROM organization_members m
JOIN users u ON m.user_id = u.id
JOIN organizations o ON m.organization_id = o.id
WHERE 1=1
  AND o.name = 'Swimply'
;
