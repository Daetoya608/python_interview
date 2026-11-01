"""Локальная атомарность и savepoint на SQLite, без внешних ресурсов."""
import sqlite3


def main():
    db = sqlite3.connect(":memory:", isolation_level=None)
    try:
        db.executescript("CREATE TABLE accounts(id INTEGER PRIMARY KEY, balance INTEGER NOT NULL CHECK(balance>=0)); INSERT INTO accounts VALUES(1,1000),(2,500);")
        db.execute("BEGIN")
        try:
            db.execute("UPDATE accounts SET balance=balance+100 WHERE id=2")
            db.execute("UPDATE accounts SET balance=balance-9999 WHERE id=1")
            db.commit()
        except sqlite3.IntegrityError:
            db.rollback()
        assert db.execute("SELECT balance FROM accounts ORDER BY id").fetchall() == [(1000,), (500,)]
        print("ROLLBACK: both balances unchanged")
        db.execute("BEGIN")
        db.execute("UPDATE accounts SET balance=balance+100 WHERE id=1")
        db.execute("SAVEPOINT optional_step")
        db.execute("UPDATE accounts SET balance=balance+200 WHERE id=2")
        db.execute("ROLLBACK TO SAVEPOINT optional_step")
        db.execute("RELEASE SAVEPOINT optional_step")
        db.commit()
        assert db.execute("SELECT balance FROM accounts ORDER BY id").fetchall() == [(1100,), (500,)]
        print("SAVEPOINT: first change committed, second rolled back")
    finally:
        db.close()


if __name__ == "__main__":
    main()
