from __future__ import annotations
import sqlite3, time
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "erp.db"

def _connect():
    return sqlite3.connect(DB_PATH)

def init_memory_tables():
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tool_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts INTEGER,
                tool_name TEXT,
                params TEXT,
                result TEXT,
                ok INTEGER
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS approvals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts INTEGER,
                policy TEXT,
                action TEXT,
                risk REAL,
                status TEXT DEFAULT 'PENDING'
            );
            """
        )
        conn.commit()

def log_tool_call(tool_name: str, params: str, result: str, ok: bool):
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO tool_calls (ts, tool_name, params, result, ok) VALUES (?, ?, ?, ?, ?);",
                    (int(time.time()), tool_name, params, result, 1 if ok else 0))
        conn.commit()

def create_approval(policy: str, action: str, risk: float) -> int:
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO approvals (ts, policy, action, risk, status) VALUES (?, ?, ?, ?, 'PENDING');",
                    (int(time.time()), policy, action, risk))
        conn.commit()
        return cur.lastrowid
