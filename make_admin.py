import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "expense.db")

conn = sqlite3.connect(DB_PATH)

# Make admin
conn.execute("""
    UPDATE users
    SET role = 'admin'
    WHERE email = ?
""", ("email@gmail.com",))
conn.commit()
print("Admin role updated")

