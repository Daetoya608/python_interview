-- A window preserves each selected order instead of collapsing the group.
SELECT id, customer_id, amount_cents,
       SUM(amount_cents) OVER (PARTITION BY customer_id) AS customer_total,
       ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY amount_cents DESC, id) AS row_no,
       RANK() OVER (PARTITION BY customer_id ORDER BY amount_cents DESC) AS price_rank,
       DENSE_RANK() OVER (PARTITION BY customer_id ORDER BY amount_cents DESC) AS dense_price_rank
FROM orders
WHERE status = 'paid' AND customer_id IS NOT NULL
ORDER BY customer_id, id;

-- Explicit ROWS frame for a running sum; LAG reads the previous row.
SELECT id, customer_id, amount_cents,
       SUM(amount_cents) OVER (
           PARTITION BY customer_id ORDER BY created_at, id
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS running_total,
       LAG(amount_cents) OVER (PARTITION BY customer_id ORDER BY created_at, id) AS previous_amount
FROM orders
WHERE status = 'paid' AND customer_id IS NOT NULL
ORDER BY customer_id, created_at, id;

-- Window values are filtered in an outer query.
WITH ranked AS (
    SELECT id, customer_id, amount_cents,
           ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY amount_cents DESC, id) AS rn
    FROM orders
    WHERE status = 'paid' AND customer_id IS NOT NULL
)
SELECT id, customer_id, amount_cents FROM ranked WHERE rn <= 1 ORDER BY customer_id;

-- Rank ties: for all Anna's orders, amounts 10000, 10000, 5000.
SELECT id, amount_cents,
       ROW_NUMBER() OVER (ORDER BY amount_cents DESC, id) AS row_no,
       RANK() OVER (ORDER BY amount_cents DESC) AS price_rank,
       DENSE_RANK() OVER (ORDER BY amount_cents DESC) AS dense_price_rank
FROM orders WHERE customer_id = 1
ORDER BY amount_cents DESC, id;
