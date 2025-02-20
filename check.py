import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()

c.execute("PRAGMA table_info(users)")
columns = c.fetchall()

for column in columns:
    print(column)

conn.close()
