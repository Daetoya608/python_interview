import sqlite3


class Notes:
    def __init__(self, path):
        self.connection = sqlite3.connect(path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, title TEXT NOT NULL)"
        )
        self.connection.commit()

    def add(self, title):
        if not title.strip():
            raise ValueError("title must not be empty")
        with self.connection:
            result = self.connection.execute("INSERT INTO notes (title) VALUES (?)", (title,))
        return result.lastrowid

    def get(self, note_id):
        row = self.connection.execute("SELECT title FROM notes WHERE id = ?", (note_id,)).fetchone()
        return row[0] if row is not None else None

    def close(self):
        self.connection.close()
