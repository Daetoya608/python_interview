-- Five rows; only two known discounts; two distinct non-NULL customer IDs.
SELECT COUNT(*) AS order_count,
       COUNT(discount_cents) AS known_discounts,
       COUNT(DISTINCT customer_id) AS known_customers,
       SUM(amount_cents) AS total_cents,
       AVG(discount_cents) AS average_known_discount
FROM orders;

-- WHERE filters rows; HAVING filters the resulting groups.
SELECT customer_id, COUNT(*) AS paid_orders, SUM(amount_cents) AS paid_cents
FROM orders
WHERE status = 'paid' AND customer_id IS NOT NULL
GROUP BY customer_id
HAVING SUM(amount_cents) >= 20000
ORDER BY paid_cents DESC, customer_id;

-- The view includes Vera with zero orders and zero total.
SELECT id, name, paid_orders, paid_cents FROM paid_customer_totals ORDER BY id;

-- COUNT(*) counts the NULL-extended row; COUNT(o.id) does not.
SELECT c.name, COUNT(*) AS joined_rows, COUNT(o.id) AS order_count
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id
GROUP BY c.id, c.name
ORDER BY c.id;

-- Empty input without GROUP BY: COUNT=0, SUM=NULL, coalesced SUM=0.
SELECT COUNT(*) AS count_empty,
       SUM(amount_cents) AS sum_empty,
       COALESCE(SUM(amount_cents), 0) AS total_or_zero
FROM orders WHERE id < 0;

-- DISTINCT amounts would lose two genuinely separate equal-price orders.
SELECT SUM(amount_cents) AS correct_total,
       SUM(DISTINCT amount_cents) AS different_meaning
FROM orders WHERE customer_id = 1 AND status = 'paid';

-- Minimum and maximum among all orders.
SELECT MIN(amount_cents) AS minimum_cents, MAX(amount_cents) AS maximum_cents
FROM orders;
