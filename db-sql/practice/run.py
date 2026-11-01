"""Запуск SQL-примеров в независимых SQLite in-memory базах, без сторонних пакетов."""

import argparse
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parent


def statements(text):
    """Учитываем CREATE TRIGGER ... BEGIN ... END, а не делим текст по каждому ';'."""
    buffer = ""
    for line in text.splitlines(keepends=True):
        buffer += line
        if sqlite3.complete_statement(buffer):
            yield buffer
            buffer = ""
    if any(line.strip() and not line.lstrip().startswith("--") for line in buffer.splitlines()):
        raise ValueError("Unfinished SQL statement")


def run(path):
    connection = sqlite3.connect(":memory:", isolation_level=None)
    try:
        connection.executescript((ROOT / "schema.sqlite.sql").read_text(encoding="utf-8"))
        print(f"\n=== {path.name} ===")
        for number, statement in enumerate(statements(path.read_text(encoding="utf-8")), 1):
            cursor = connection.execute(statement)
            if cursor.description:
                print(f"[{number}]", " | ".join(column[0] for column in cursor.description))
                rows = cursor.fetchall()
                for row in rows:
                    print(row)
                print(f"rows: {len(rows)}")
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="Names such as 02_joins.sql; default: all numbered files")
    args = parser.parse_args()
    if sqlite3.sqlite_version_info < (3, 39, 0):
        parser.error("SQLite 3.39+ is required for RIGHT/FULL JOIN; use a Python with newer SQLite")
    available = {path.name: path for path in sorted(ROOT.glob("[0-9][0-9]_*.sql"))}
    unknown = set(args.files) - available.keys()
    if unknown:
        parser.error("Unknown example: " + ", ".join(sorted(unknown)))
    print("SQLite", sqlite3.sqlite_version)
    for path in ([available[name] for name in args.files] if args.files else available.values()):
        run(path)


if __name__ == "__main__":
    main()
