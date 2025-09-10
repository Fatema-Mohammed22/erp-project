# app/rag_supplier.py
import sqlite3
import pandas as pd

class RAGSupplierRetriever:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)

    def get_supplier_documents(self):
        query = """
        SELECT * 
        FROM documents 
        WHERE module = 'inventory' AND tags LIKE '%supplier%'
        """
        return pd.read_sql_query(query, self.conn)

if __name__ == "__main__":
    retriever = RAGSupplierRetriever("../data/erp_sample.db")
    df = retriever.get_supplier_documents()
    if df.empty:
        print("No supplier documents found.")
    else:
        print("Supplier Documents:")
        print(df[['id', 'path', 'tags', 'created_at']])
