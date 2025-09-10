# main_demo.py
import sqlite3
import pandas as pd
from app.analytics_agent import AnalyticsAgent
from app.rag_supplier import RAGSupplierRetriever

# -------------------------------
# 1. Analytics Agent
# -------------------------------
print("\n=== Analytics: Sales by Customer ===")
db_path = "data/erp_sample.db"
agent = AnalyticsAgent(db_path)

# استعلام إجمالي المبيعات وعدد الطلبات لكل عميل
sql_sales = """
SELECT c.name AS customer_name,
       COUNT(o.id) AS num_orders,
       SUM(o.total) AS total_sales
FROM orders o
JOIN customers c ON o.customer_id = c.id
GROUP BY c.name
ORDER BY total_sales DESC
"""
df_sales = agent.query(sql_sales)
print(df_sales.head(10))  # عرض أفضل 10 عملاء حسب المبيعات

# -------------------------------
# 2. Inventory Agent
# -------------------------------
print("\n=== Inventory: Stock Monitoring & Auto-Reorder ===")
conn = sqlite3.connect(db_path)
df_stock = pd.read_sql_query("SELECT id, product_id, qty_on_hand, reorder_point FROM stock", conn)
print("Current Stock Levels:")
print(df_stock.head(10))

# المنتجات التي تحتاج إعادة طلب
df_reorder = df_stock[df_stock["qty_on_hand"] < df_stock["reorder_point"]]
print("\nProducts to Reorder:")
print(df_reorder)

# إنشاء طلب شراء وهمي لكل منتج ناقص
for _, row in df_reorder.iterrows():
    print(f"Auto-reorder triggered for product_id {row['product_id']} (current: {row['qty_on_hand']})")

conn.close()

# -------------------------------
# 3. RAG Supplier Retriever
# -------------------------------
print("\n=== RAG Supplier Documents ===")
retriever = RAGSupplierRetriever(db_path)
df_docs = retriever.get_supplier_documents()
if df_docs.empty:
    print("No supplier documents found.")
else:
    print(df_docs[['id', 'path', 'tags', 'created_at']])
