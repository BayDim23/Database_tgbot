import sqlite3
conn = sqlite3.connect('bot.db')

cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS users (
id INTEGER PRIMARY KEY,
username TEXT,
chat_id INTEGER)''')

conn.commit()
conn.close()

