--- Last 20 invoices
SELECT 
    invoices_id AS id,
    customer_id,
    invoices_number,
    issue_date,
    due_date,
    total_amount,
    status,
    created_at
FROM invoices
WHERE invoices_id = 1;