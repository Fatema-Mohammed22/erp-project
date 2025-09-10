--- Last 20 approvals
SELECT 
    approval_id AS id, 
    module,
    pyload_json,
    status,
    requested_by,
    decided_by,
    created_at,
    decided_at
FROM approvals 
WHERE approval_id = 1;
