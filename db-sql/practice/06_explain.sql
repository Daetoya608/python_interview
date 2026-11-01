-- SQLite uses nested scans for joins; this is not PostgreSQL EXPLAIN syntax.
EXPLAIN QUERY PLAN
SELECT c.name, o.id
FROM customers AS c
JOIN orders AS o ON o.customer_id = c.id
WHERE c.id = 1;

SELECT c.name, o.id
FROM customers AS c
JOIN orders AS o ON o.customer_id = c.id
WHERE c.id = 1
ORDER BY o.id;
