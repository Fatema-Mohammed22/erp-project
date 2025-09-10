SELECT
    order_id AS id,
    customer_id,
    order_date,
    status,
    total_amount AS total,
    created_at
FROM orders
WHERE order_id = 1;