-- User ID = 1813 gets activated
-- User ID = 8 gets deactivated
-- Swimply is b02fe057-de05-40a0-b04a-7742a1189b91

BEGIN;
  -- Adds Ariana to Swimply
  INSERT INTO organization_members (user_id, organization_id, created_at, active, updated_at) VALUES
    (1813, 'b02fe057-de05-40a0-b04a-7742a1189b91', NOW(), true, NOW());

  -- Removes Ariana from personal org
  UPDATE organization_members SET active = False
    WHERE 1=1
      AND user_id = 1813
      AND organization_id != 'b02fe057-de05-40a0-b04a-7742a1189b91'
  ;

  -- Removes James from swimply
  UPDATE organization_members SET active = False
    WHERE 1=1
      AND user_id = 8
      AND organization_id = 'b02fe057-de05-40a0-b04a-7742a1189b91'
  ;
  -- Adds James back to his personal org
  UPDATE organization_members SET active = True
    WHERE 1=1
      AND user_id = 8
      AND organization_id != 'b02fe057-de05-40a0-b04a-7742a1189b91'
  ;
END;
