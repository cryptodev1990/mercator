-- SELECT * FROM users WHERE email = 'duber@mercator.tech';
-- User ID = 1
-- Swimply is b02fe057-de05-40a0-b04a-7742a1189b91

BEGIN;
  INSERT INTO organization_members (user_id, organization_id, created_at, active, updated_at) VALUES
    (1, 'b02fe057-de05-40a0-b04a-7742a1189b91', NOW(), true, NOW());
  UPDATE organization_members SET active = False
    WHERE 1=1
      AND user_id = 1
      AND organization_id != 'b02fe057-de05-40a0-b04a-7742a1189b91'
  ;
END;


-- Move back to Mercator
BEGIN;
  UPDATE organization_members SET active = False
    WHERE 1=1
      AND user_id = 1
      AND organization_id != 'e6cef492-5069-46d3-8431-fda523caf2f6'
  ;
  UPDATE organization_members SET active = True
    WHERE 1=1
      AND user_id = 1
      AND organization_id = 'e6cef492-5069-46d3-8431-fda523caf2f6'
  ;
END;
