import sqlite3
import pandas as pd
from typing import List

# مثال على الاتصال بقاعدة البيانات
conn = sqlite3.connect("data/erp_sample.db")

# تحميل Glossary
glossary_df = pd.read_sql_query("SELECT * FROM glossary", conn)

# تحميل Documents
documents_df = pd.read_sql_query("SELECT * FROM documents", conn)

print(glossary_df.head())
print(documents_df.head())
