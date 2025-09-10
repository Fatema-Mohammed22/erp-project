import sqlite3
import os

db_path = "erp_sample.db"

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables in database:", tables)
        conn.close()
    except Exception as e:
        print("Error opening database:", e)
else:
    print("Database file not found at:", db_path)
