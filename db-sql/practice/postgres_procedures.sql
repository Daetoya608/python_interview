-- PostgreSQL only. Run in a separate session: psql -X -v ON_ERROR_STOP=1 -f postgres_procedures.sql DATABASE_URL
-- All objects and data below are temporary/transactional; ROLLBACK restores the session.
BEGIN;

CREATE TEMP TABLE accounts (
    id INTEGER PRIMARY KEY,
    balance_cents BIGINT NOT NULL CHECK (balance_cents >= 0)
);
CREATE TEMP TABLE balance_audit (
    account_id INTEGER NOT NULL,
    old_balance_cents BIGINT NOT NULL,
    new_balance_cents BIGINT NOT NULL
);
INSERT INTO accounts (id, balance_cents) VALUES (1, 10000), (2, 2000);

CREATE FUNCTION pg_temp.log_balance_change() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO balance_audit (account_id, old_balance_cents, new_balance_cents)
    VALUES (NEW.id, OLD.balance_cents, NEW.balance_cents);
    RETURN NEW;
END;
$$;

CREATE TRIGGER audit_balance
AFTER UPDATE OF balance_cents ON accounts
FOR EACH ROW
WHEN (OLD.balance_cents IS DISTINCT FROM NEW.balance_cents)
EXECUTE FUNCTION pg_temp.log_balance_change();

CREATE PROCEDURE pg_temp.transfer_money(p_from INTEGER, p_to INTEGER, p_amount BIGINT)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_from IS NULL OR p_to IS NULL OR p_from = p_to
       OR p_amount IS NULL OR p_amount <= 0 THEN
        RAISE EXCEPTION 'Invalid transfer arguments';
    END IF;

    -- A stable lock order reduces deadlock risk for concurrent transfers.
    PERFORM id FROM accounts WHERE id IN (p_from, p_to) ORDER BY id FOR UPDATE;

    UPDATE accounts SET balance_cents = balance_cents - p_amount
    WHERE id = p_from AND balance_cents >= p_amount;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Source account is missing or funds are insufficient';
    END IF;

    UPDATE accounts SET balance_cents = balance_cents + p_amount WHERE id = p_to;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Destination account is missing';
    END IF;
END;
$$;

CALL pg_temp.transfer_money(1, 2, 1500);
SELECT id, balance_cents FROM accounts ORDER BY id;
-- Expected: (1, 8500), (2, 3500).
SELECT account_id, old_balance_cents, new_balance_cents FROM balance_audit ORDER BY account_id;
-- Expected: two changes in the same transaction, not an independent audit commit.
ROLLBACK;
