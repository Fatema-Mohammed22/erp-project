import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

class AnalyticsAgent:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        os.makedirs("outputs", exist_ok=True)
        self.log_file = "outputs/analytics_log.txt"

    def query(self, sql, params=None):
        return pd.read_sql_query(sql, self.conn, params=params)

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"{timestamp} - {message}\n")
        print(message)

    def save_csv(self, df, filename):
        path = os.path.join("outputs", filename)
        df.to_csv(path, index=False)
        self.log(f"Saved CSV: {filename}")

    def plot_and_save(self, df, x_col, y_col, title, filename):
        ax = df.plot(kind='bar', x=x_col, y=y_col, title=title, figsize=(10,6))
        plt.tight_layout()
        plt.savefig(os.path.join("outputs", filename))
        plt.close()
        self.log(f"Saved plot: {filename}")

    # 1. Sales by customer
   # داخل class AnalyticsAgent
    def sales_by_customer(self):
     sql = """
    SELECT c.name AS customer_name, 
           COUNT(o.id) AS num_orders,
           SUM(o.total) AS total_sales
    FROM orders o
    JOIN customers c ON o.customer_id = c.id
    GROUP BY c.name        
    ORDER BY total_sales DESC
    """
     df = self.query(sql)
     self.save_csv(df, "sales_by_customer.csv")
     self.plot_and_save(df, "customer_name", "total_sales", "Sales by Customer", "sales_by_customer.png")
     return df


    # 2. Top products
    def top_products(self, top_n=10):
        sql = """
        SELECT p.name as product_name, SUM(oi.quantity * oi.price) as total_sales
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        GROUP BY p.name
        ORDER BY total_sales DESC
        LIMIT ?
        """
        df = self.query(sql, params=(top_n,))
        self.save_csv(df, "top_products.csv")
        self.plot_and_save(df, "product_name", "total_sales", f"Top {top_n} Products", "top_products.png")
        return df

    # 3. Detect anomalies (example: orders with unusually high total)
    def detect_anomalies(self):
        df = self.query("SELECT id, customer_id, total, created_at FROM orders")
        threshold = df['total'].mean() + 3*df['total'].std()
        anomalies = df[df['total'] > threshold]
        self.save_csv(anomalies, "anomalous_orders.csv")
        self.log(f"Detected {len(anomalies)} anomalous orders")
        return anomalies

    # 4. Lead Scores
    def export_lead_scores(self):
        df = self.query("SELECT customer_name, contact_email, score FROM leads ORDER BY score DESC")
        self.save_csv(df, "lead_scores.csv")
        self.log(f"Exported {len(df)} lead scores")
        return df


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "data", "erp_sample.db")

    print(f"Using database at: {db_path}")
    agent = AnalyticsAgent(db_path)

    while True:
        print("\n=== Analytics Menu ===")
        print("1. Sales by customer")
        print("2. Top Products")
        print("3. Detect Anomalies")
        print("4. Export Lead Scores")
        print("0. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            print(agent.sales_by_customer())
        elif choice == "2":
            top_n = int(input("How many top products to show? "))
            print(agent.top_products(top_n))
        elif choice == "3":
            print(agent.detect_anomalies())
        elif choice == "4":
            print(agent.export_lead_scores())
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid choice, try again.")
