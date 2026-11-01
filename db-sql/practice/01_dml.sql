-- SELECT: explicit columns, filter and stable ordering.
SELECT id, amount_cents, status
FROM orders
WHERE status = 'paid' AND amount_cents >= 10000
ORDER BY amount_cents DESC, id
LIMIT 10;

-- Changes in this example are rolled back.
BEGIN;
INSERT INTO customers (id, name, city) VALUES (4, 'Dima', 'Kazan');
INSERT INTO orders (id, customer_id, amount_cents, status, created_at)
VALUES (401, 4, 7500, 'new', '2026-10-05');

UPDATE orders SET status = 'paid' WHERE id = 401;
SELECT id, status FROM orders WHERE id = 401;

DELETE FROM orders WHERE id = 401;
SELECT COUNT(*) AS remaining FROM orders WHERE id = 401;
ROLLBACK;

SELECT COUNT(*) AS restored_customers FROM customers;
