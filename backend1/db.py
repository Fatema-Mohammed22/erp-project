import os
import sqlite3
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("SQLITE_PATH", "./data/erp_sample.db")

def _connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@contextmanager
def get_conn():
    conn = _connect()
    try:
        yield conn
    finally:
        conn.close()

def query_all(sql: str, params: tuple = ()):
    with get_conn() as conn:
        cur = conn.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]

def execute(sql: str, params: tuple = ()):
    with get_conn() as conn:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid
