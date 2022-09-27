-- SELECT * FROM users WHERE email = 'john@swimply.com';
-- User ID = 13
-- Swimply is b02fe057-de05-40a0-b04a-7742a1189b91

BEGIN;
  INSERT INTO organization_members (user_id, organization_id, created_at, active, updated_at) VALUES
    (13, 'b02fe057-de05-40a0-b04a-7742a1189b91', NOW(), true, NOW());
  UPDATE organization_members SET active = False
    WHERE 1=1
      AND user_id = 13
      AND organization_id != 'b02fe057-de05-40a0-b04a-7742a1189b91'
  ;
END;
