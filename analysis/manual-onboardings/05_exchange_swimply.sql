-- Tyler / User ID = 14 gets activated
-- John / User ID = 13 gets deactivated
-- Swimply is b02fe057-de05-40a0-b04a-7742a1189b91
BEGIN;
  -- Adds Tyler to Swimply
  INSERT INTO organization_members (user_id, organization_id, created_at, active, updated_at) VALUES
    (14, 'b02fe057-de05-40a0-b04a-7742a1189b91', NOW(), true, NOW());
  -- Removes Tyler from personal org
  UPDATE organization_members SET active = False
    WHERE 1=1
      AND user_id = 14
      AND organization_id != 'b02fe057-de05-40a0-b04a-7742a1189b91'
  ;
  -- Removes John from swimply
  UPDATE organization_members SET active = False
    WHERE 1=1
      AND user_id = 13
      AND organization_id = 'b02fe057-de05-40a0-b04a-7742a1189b91'
  ;
  -- Adds John back to his personal org
  UPDATE organization_members SET active = True
    WHERE 1=1
      AND user_id = 13
      AND organization_id != 'b02fe057-de05-40a0-b04a-7742a1189b91'
  ;
END;
