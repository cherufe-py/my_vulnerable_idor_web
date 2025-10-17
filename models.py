import sqlite3

from flask import g

APP_DB = 'example.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(APP_DB)
        db.row_factory = sqlite3.Row
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def get_setting(key, default=None):
    row = query_db('SELECT value FROM settings WHERE key = ?', (key,), one=True)
    return row['value'] if row else default


def set_setting(key, value):
    db = get_db()
    # upsert: try update, if 0 rows affected insert
    cur = db.execute('UPDATE settings SET value = ? WHERE key = ?', (value, key))
    if cur.rowcount == 0:
        db.execute('INSERT INTO settings (key, value) VALUES (?, ?)', (key, value))
    db.commit()
