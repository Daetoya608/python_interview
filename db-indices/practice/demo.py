"""SQLite: план до/после индекса; без постоянной БД и внешних пакетов."""
import sqlite3


def main():
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("CREATE TABLE orders(id INTEGER PRIMARY KEY, customer_id INTEGER, amount_cents INTEGER)")
        connection.executemany(
            "INSERT INTO orders VALUES (?, ?, ?)",
            ((i, i % 1000, i * 10) for i in range(1, 20001)),
        )
        connection.commit()
        sql = "SELECT amount_cents FROM orders WHERE customer_id = ? ORDER BY amount_cents"
        before = connection.execute(sql, (42,)).fetchall()
        print("BEFORE", connection.execute("EXPLAIN QUERY PLAN " + sql, (42,)).fetchall())
        connection.execute("CREATE INDEX idx_cover ON orders(customer_id, amount_cents)")
        after = connection.execute(sql, (42,)).fetchall()
        print("AFTER", connection.execute("EXPLAIN QUERY PLAN " + sql, (42,)).fetchall())
        assert before == after and len(after) == 20
        print("Same 20 rows; compare scan/search/covering access, not a universal timing ratio.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
