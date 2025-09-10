import streamlit as st
from app.analytics_agent import AnalyticsAgent
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "data", "erp_sample.db")
agent = AnalyticsAgent(db_path)

st.title("📊 ERP Analytics Dashboard")

if st.button("Sales by Customer"):
    st.dataframe(agent.sales_by_customer())

if st.button("Top Products"):
    st.dataframe(agent.top_products(10))

if st.button("Detect Anomalies"):
    st.dataframe(agent.detect_anomalies())

if st.button("Lead Scores"):
    st.dataframe(agent.export_lead_scores())
