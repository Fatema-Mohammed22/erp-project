--- Last 20 products
SELECT
    product_id AS id,
    sku,
    product_name AS name,
    unit_price AS price,
    description
FROM products
WHERE product_id = 1;