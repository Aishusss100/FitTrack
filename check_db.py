# check_db.py
import sqlite3

def check_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = c.fetchone()
    if table_exists:
        print("Table exists.")
    else:
        print("Table does not exist.")
    conn.close()

check_db()
