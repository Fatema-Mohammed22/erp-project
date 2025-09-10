import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import joblib
import os

class LeadScoringModel:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)

    def load_data(self):
        # تحميل بيانات العملاء والمبيعات
        leads = pd.read_sql_query("SELECT * FROM leads", self.conn)
        orders = pd.read_sql_query("SELECT * FROM orders", self.conn)

        # حساب سمات لكل lead
        orders_grouped = orders.groupby('customer_id').agg(
            total_orders=('id', 'count'),
            total_sales=('total', 'sum'),
            last_order_date=('created_at', 'max')
        ).reset_index()

        data = leads.merge(orders_grouped, left_on='id', right_on='customer_id', how='left')
        data['total_orders'].fillna(0, inplace=True)
        data['total_sales'].fillna(0, inplace=True)
        data['last_order_date'] = pd.to_datetime(data['last_order_date'])
        data['days_since_last_order'] = (pd.Timestamp.now() - data['last_order_date']).dt.days
        data['days_since_last_order'].fillna(999, inplace=True)  # لم يسبق لهم طلب

        # تحويل status إلى رقم
        le = LabelEncoder()
        data['status_encoded'] = le.fit_transform(data['status'])

        features = ['total_orders', 'total_sales', 'days_since_last_order']
        target = 'status_encoded'

        return data[features], data[target], le

    def train_model(self):
        X, y, le = self.load_data()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # تقييم النموذج
        y_pred = model.predict(X_test)
        print(classification_report(y_test, y_pred))

        # حفظ النموذج
        os.makedirs("models", exist_ok=True)
        joblib.dump(model, "models/lead_scoring_model.pkl")
        joblib.dump(le, "models/lead_status_encoder.pkl")
        print("Model saved in 'models/' folder.")

if __name__ == "__main__":
    scorer = LeadScoringModel("../data/erp_sample.db")
    scorer.train_model()
