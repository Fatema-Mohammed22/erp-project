import sqlite3
import pandas as pd
from datetime import datetime

class InventoryAgent:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def get_stock_levels(self):
        """جلب جميع مستويات المخزون الحالية"""
        query = "SELECT s.id, p.name AS product_name, s.qty_on_hand, s.reorder_point, sp.supplier_id FROM stock s JOIN products p ON s.product_id = p.id LEFT JOIN supplier_products sp ON p.id = sp.product_id"
        return pd.read_sql_query(query, self.conn)

    def check_reorder(self):
        """التحقق من المنتجات التي وصلت لنقطة إعادة الطلب"""
        df = self.get_stock_levels()
        low_stock = df[df['qty_on_hand'] <= df['reorder_point']]
        return low_stock

    def create_purchase_orders(self):
        """إنشاء أوامر شراء تلقائية للمخزون المنخفض"""
        low_stock = self.check_reorder()
        orders = []
        for _, row in low_stock.iterrows():
            qty_to_order = row['reorder_point'] * 2 - row['qty_on_hand']  # كمية مرنة لإعادة التخزين
            if qty_to_order > 0 and pd.notna(row['supplier_id']):
                # حفظ أمر الشراء في جدول purchase_orders
                self.cursor.execute(
                    "INSERT INTO purchase_orders (supplier_id, status, created_at) VALUES (?, ?, ?)",
                    (int(row['supplier_id']), 'auto-generated', datetime.now())
                )
                po_id = self.cursor.lastrowid
                # حفظ عناصر الطلب
                self.cursor.execute(
                    "INSERT INTO po_items (po_id, product_id, quantity, unit_cost) VALUES (?, ?, ?, ?)",
                    (po_id, row['id'], qty_to_order, 0)  # 0 يمكن استبداله بالتكلفة الافتراضية
                )
                orders.append({
                    'product': row['product_name'],
                    'qty_ordered': qty_to_order,
                    'supplier_id': int(row['supplier_id']),
                    'po_id': po_id
                })
        self.conn.commit()
        return orders

    def run_inventory_check(self):
        """تشغيل الفحص وإنشاء أوامر شراء تلقائية"""
        low_stock = self.check_reorder()
        print("Low stock products:")
        print(low_stock[['product_name', 'qty_on_hand', 'reorder_point']])
        orders = self.create_purchase_orders()
        if orders:
            print("\nAuto-generated Purchase Orders:")
            for o in orders:
                print(f"PO #{o['po_id']}: {o['product']} x{o['qty_ordered']} to Supplier {o['supplier_id']}")
        else:
            print("\nNo auto-orders generated. Stock levels are sufficient.")

if __name__ == "__main__":
    agent = InventoryAgent("../data/erp_sample.db")
    agent.run_inventory_check()
