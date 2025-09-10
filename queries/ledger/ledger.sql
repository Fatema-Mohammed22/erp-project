--- Last 20 ledger entries
SELECT 
    ledger_id AS id,
    entry_type,
    created_at
FROM ledger
WHERE ledger_id = 1;