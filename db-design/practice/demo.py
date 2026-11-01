"""Проверка FK, one-to-one, many-to-many и исторической цены в SQLite."""
from pathlib import Path
import sqlite3


def main():
    db = sqlite3.connect(":memory:", isolation_level=None)
    try:
        db.executescript(Path(__file__).with_name("schema.sql").read_text(encoding="utf-8"))
        db.execute("INSERT INTO products VALUES(2,'Pen',100)")
        invalid = [
            "INSERT INTO orders VALUES(2,999)",
            "INSERT INTO profiles VALUES(2,1,'Duplicate')",
            "INSERT INTO order_items VALUES(1,1,1,1000)",
            "INSERT INTO order_items VALUES(1,2,0,1000)",
        ]
        for sql in invalid:
            try:
                db.execute(sql)
            except sqlite3.IntegrityError:
                print("Rejected:", sql)
            else:
                raise AssertionError("Constraint did not reject invalid data")
        db.execute("UPDATE products SET current_price_cents=9999 WHERE id=1")
        total = db.execute("SELECT SUM(quantity*unit_price_cents) FROM order_items WHERE order_id=1").fetchone()[0]
        assert total == 2400
        print("Historical order total remains", total)
    finally:
        db.close()


if __name__ == "__main__":
    main()
