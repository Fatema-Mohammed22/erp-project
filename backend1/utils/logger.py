import sqlite3
import os

DB_PATH = os.getenv("SQLITE_PATH", "./data/erp_sample.db")

def log_tool_call(agent: str, tool_name: str, input_json: str, output_json: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tool_calls (agent, tool_name, input_json, output_json, created_at)
        VALUES (?, ?, ?, ?, datetime('now'))
    """, (agent, tool_name, input_json, output_json))
    conn.commit()
    conn.close()
