import sqlite3
import pandas as pd
import os

db_path = "data/erp_sample.db"  # تأكد إنه نفس اسم الملف في مشروعك

if not os.path.exists(db_path):
    raise FileNotFoundError(f"Database file not found at {db_path}")

# الاتصال بقاعدة البيانات
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# جلب كل أسماء الجداول
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in cursor.fetchall()]
print("Tables found:", tables)

# طباعة أول 5 صفوف من كل جدول
for table in tables:
    print(f"\nTable: {table}")
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 5;", conn)
        print(df)
    except Exception as e:
        print(f"Could not read table {table}: {e}")

conn.close()
