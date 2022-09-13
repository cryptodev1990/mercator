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

