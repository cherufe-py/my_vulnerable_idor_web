import os
import sqlite3

APP_DB = 'example.db'


def init_db():
    if os.path.exists(APP_DB):
        os.remove(APP_DB)

    db = sqlite3.connect(APP_DB)
    cur = db.cursor()

    cur.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cur.execute('''
        CREATE TABLE files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            filename TEXT NOT NULL,
            content_type TEXT,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cur.execute('''
        CREATE TABLE settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    cur.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('alice', 'alicepass'))
    cur.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('bob', 'bobpass'))

    cur.execute('INSERT INTO settings (key, value) VALUES (?, ?)', ('check_ownership', 'false'))

    db.commit()
    db.close()
    print('Database initialized (example.db). Users seeded, files table empty, settings created.')


if __name__ == '__main__':
    init_db()
