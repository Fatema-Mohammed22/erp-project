--- Last 20 customers
SELECT 
    customer_id AS id, 
    customer_name AS name,
    email,
    phone,
    created_at,
FROM customers 
WHERE customer_id = 1;