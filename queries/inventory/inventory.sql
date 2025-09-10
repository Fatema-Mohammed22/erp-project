--- Products with low stock (Less than 10 unites)
SELECT 
    invontory_id AS id,
    product_id, 
    quantity,
    location, 
    last_updated
FROM invontory
WHERE quantity < 10
ORDER BY quantity ASC;
WHERE inventory_id = 1;
