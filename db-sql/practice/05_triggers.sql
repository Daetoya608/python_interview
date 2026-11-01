-- SQLite-specific body syntax. No stored procedures are used here.
CREATE TRIGGER audit_order_status
AFTER UPDATE OF status ON orders
FOR EACH ROW
WHEN OLD.status <> NEW.status
BEGIN
    INSERT INTO order_status_history (order_id, old_status, new_status)
    VALUES (OLD.id, OLD.status, NEW.status);
END;

BEGIN;
UPDATE orders SET status = 'cancelled' WHERE id = 101;
-- Setting the same value does not add another audit row.
UPDATE orders SET status = 'cancelled' WHERE id = 101;
SELECT order_id, old_status, new_status FROM order_status_history ORDER BY id;
ROLLBACK;

-- The audit insert belonged to the same transaction and is rolled back too.
SELECT id, status FROM orders WHERE id = 101;
SELECT COUNT(*) AS history_after_rollback FROM order_status_history;
