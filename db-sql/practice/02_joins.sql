-- INNER: only matching pairs (4 rows).
SELECT c.name, o.id AS order_id
FROM customers AS c
INNER JOIN orders AS o ON o.customer_id = c.id
ORDER BY c.id, o.id;

-- LEFT: Vera remains with a NULL order (5 rows).
SELECT c.name, o.id AS order_id
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id
ORDER BY c.id, o.id;

-- RIGHT: all orders, including guest order 301 (5 rows).
SELECT c.name, o.id AS order_id
FROM customers AS c
RIGHT JOIN orders AS o ON o.customer_id = c.id
ORDER BY o.id;

-- FULL: unmatched customer and unmatched guest order (6 rows).
SELECT c.name, o.id AS order_id
FROM customers AS c
FULL OUTER JOIN orders AS o ON o.customer_id = c.id
ORDER BY COALESCE(c.id, 999), o.id;

-- CROSS: Cartesian product (3 * 5 = 15 rows).
SELECT COUNT(*) AS pair_count FROM customers CROSS JOIN orders;

-- SELF: the same table participates in two roles.
SELECT c.name, referrer.name AS referred_by
FROM customers AS c
LEFT JOIN customers AS referrer ON referrer.id = c.referrer_id
ORDER BY c.id;

-- Predicate in ON preserves customers without paid orders.
SELECT c.name, o.id AS paid_order_id
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id AND o.status = 'paid'
ORDER BY c.id, o.id;

-- Predicate in WHERE removes Vera's NULL-extended row.
SELECT c.name, o.id AS paid_order_id
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id
WHERE o.status = 'paid'
ORDER BY c.id, o.id;

-- SEMI join expressed through EXISTS: one row per customer.
SELECT c.name FROM customers AS c
WHERE EXISTS (SELECT 1 FROM orders AS o WHERE o.customer_id = c.id)
ORDER BY c.id;

-- ANTI join through NOT EXISTS: customers without orders.
SELECT c.name FROM customers AS c
WHERE NOT EXISTS (SELECT 1 FROM orders AS o WHERE o.customer_id = c.id)
ORDER BY c.id;

-- NOT IN is not equivalent here: the subquery contains NULL from guest order 301.
SELECT c.name FROM customers AS c
WHERE c.id NOT IN (SELECT o.customer_id FROM orders AS o)
ORDER BY c.id;
