PRAGMA foreign_keys = ON;

CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    referrer_id INTEGER REFERENCES customers(id)
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    amount_cents INTEGER NOT NULL CHECK (amount_cents >= 0),
    discount_cents INTEGER CHECK (discount_cents >= 0),
    status TEXT NOT NULL CHECK (status IN ('new', 'paid', 'cancelled')),
    created_at TEXT NOT NULL
);

CREATE INDEX idx_orders_customer_id ON orders(customer_id);

CREATE TABLE order_status_history (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    old_status TEXT NOT NULL,
    new_status TEXT NOT NULL
);

INSERT INTO customers (id, name, city, referrer_id) VALUES
    (1, 'Anna', 'Moscow', NULL),
    (2, 'Boris', 'Saint Petersburg', 1),
    (3, 'Vera', 'Moscow', 1);

INSERT INTO orders (id, customer_id, amount_cents, discount_cents, status, created_at) VALUES
    (101, 1, 10000, NULL, 'paid', '2026-10-01'),
    (102, 1, 10000, 500, 'paid', '2026-10-02'),
    (103, 1, 5000, NULL, 'cancelled', '2026-10-03'),
    (201, 2, 20000, NULL, 'paid', '2026-10-01'),
    (301, NULL, 3000, 0, 'paid', '2026-10-04');

CREATE VIEW paid_customer_totals AS
SELECT c.id, c.name,
       COUNT(o.id) AS paid_orders,
       COALESCE(SUM(o.amount_cents), 0) AS paid_cents
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id AND o.status = 'paid'
GROUP BY c.id, c.name;
