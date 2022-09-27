-- How many shapes have folks drawn?
SELECT email
, COUNT(DISTINCT s.uuid) AS num_shapes
FROM shapes s
JOIN organizations o
ON s.organization_id = o.id
JOIN organization_members om
ON o.id = om.organization_id
JOIN users u
ON u.id = om.user_id
GROUP BY 1
ORDER BY 2 DESC
;

-- Shapes per user
SELECT email
, o.name
, o.id AS organization_uuid
, COUNT(*) AS num
FROM shapes s
JOIN organizations o
ON s.organization_id = o.id
JOIN organization_members om
ON o.id = om.organization_id
JOIN users u
ON u.id = om.user_id
WHERE 1=1
  AND om.active
GROUP BY 1, 2, 3
;

-- Shape count by org
SELECT o.name
, o.id AS organization_uuid
, COUNT(DISTINCT s.uuid) AS num
FROM shapes s
JOIN organizations o
ON s.organization_id = o.id
JOIN organization_members om
ON o.id = om.organization_id
JOIN users u
ON u.id = om.user_id
WHERE 1=1
  AND om.active
  AND s.deleted_at IS NULL
GROUP BY 1, 2
ORDER BY 3 DESC
;

-- Count duplicate shapes
WITH freq AS (
SELECT geom
, COUNT(DISTINCT s.uuid) AS num
FROM shapes s
JOIN organizations o
ON s.organization_id = o.id
JOIN organization_members om
ON o.id = om.organization_id
JOIN users u
ON u.id = om.user_id
WHERE 1=1
  AND o.name = 'Swimply'
GROUP BY geom
)
SELECT num
, COUNT(*)
FROM freq
GROUP BY 1
ORDER BY 2 DESC
;

