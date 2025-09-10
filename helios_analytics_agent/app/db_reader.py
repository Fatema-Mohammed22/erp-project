import sqlite3
import pandas as pd

DB_PATH = "data/erp_sample.db"

class DBReader:
    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path)

    def list_tables(self):
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = pd.read_sql(query, self.conn)
        return tables['name'].tolist()

    def read_table(self, table_name):
        query = f"SELECT * FROM {table_name};"
        return pd.read_sql(query, self.conn)

    # تحليل المبيعات حسب الزبون
    def sales_by_customer(self):
        query = """
        SELECT c.name AS customer, SUM(o.total) AS total_sales
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        GROUP BY c.name
        ORDER BY total_sales DESC;
        """
        return pd.read_sql(query, self.conn)

    # تحليل المبيعات حسب المنتج
    def sales_by_product(self):
        query = """
        SELECT p.name AS product, SUM(oi.quantity * oi.price) AS total_sales
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        GROUP BY p.name
        ORDER BY total_sales DESC;
        """
        return pd.read_sql(query, self.conn)

    # تحليل المخزون
    def stock_overview(self):
        query = """
        SELECT p.name AS product, s.qty_on_hand, s.reorder_point
        FROM stock s
        JOIN products p ON s.product_id = p.id;
        """
        return pd.read_sql(query, self.conn)


if __name__ == "__main__":
    db = DBReader()
    print("Tables in database:", db.list_tables())
    
    print("\nSales by Customer:")
    print(db.sales_by_customer().head())

    print("\nSales by Product:")
    print(db.sales_by_product().head())

    print("\nStock Overview:")
    print(db.stock_overview().head())
