from __future__ import annotations
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import sqlite3, json, re
from pathlib import Path
from ..mcp.registry import MCPTool, global_registry
from ..memory.state import log_tool_call

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "erp.db"

ALLOWED_TABLES = {
    "customers","leads","orders","order_items","products","tickets",
    "invoices","invoice_lines","invoice_orders","payments","payment_allocations",
    "ledger_entries","ledger_lines","chart_of_accounts","stock","stock_movements",
    "suppliers","supplier_products","purchase_orders","po_items","po_receipts",
    "glossary","documents","customer_kv","approvals","tool_calls","conversations","messages"
}

class SQLReadParams(BaseModel):
    sql: str = Field(description="A SELECT-only SQL query using allowed tables")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Optional parameter dict for ? placeholders")

def _check_select(sql: str):
    s = sql.strip().upper()
    if not s.startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed in sales_sql_read/finance_sql_read/inventory_sql_read")
    tables = re.findall(r"\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*)|\bJOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql, flags=re.I)
    flat = [t[0] or t[1] for t in tables]
    for t in flat:
        if t not in ALLOWED_TABLES:
            raise ValueError(f"Table '{t}' not allowed")

def _execute_select(sql: str, params: Optional[Dict[str, Any]]):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        if params:
            cur.execute(sql, tuple(params.values()))
        else:
            cur.execute(sql)
        rows = [dict(r) for r in cur.fetchall()]
    return rows

def make_sql_read_tool(name: str, description: str):
    def handler(model: SQLReadParams):
        _check_select(model.sql)
        res = _execute_select(model.sql, model.params)
        log_tool_call(name, json.dumps(model.dict()), json.dumps({"rows": len(res)}), True)
        return res
    tool = MCPTool(name=name, description=description, ParamModel=SQLReadParams, handler=handler)
    global_registry.register(tool)
    return tool

class SQLInsertParams(BaseModel):
    table: str
    values: Dict[str, Any]

def _check_table(table: str):
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Table '{table}' not allowed")

def _execute_insert(table: str, values: Dict[str, Any]):
    keys = list(values.keys())
    placeholders = ",".join(["?"]*len(keys))
    cols = ",".join(keys)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"INSERT INTO {table} ({cols}) VALUES ({placeholders});", tuple(values[k] for k in keys))
        conn.commit()
        return {"last_row_id": cur.lastrowid}

def make_sql_write_tool(name: str, description: str):
    def handler(model: SQLInsertParams):
        _check_table(model.table)
        res = _execute_insert(model.table, model.values)
        log_tool_call(name, json.dumps(model.dict()), json.dumps(res), True)
        return res
    tool = MCPTool(name=name, description=description, ParamModel=SQLInsertParams, handler=handler)
    global_registry.register(tool)
    return tool

sales_sql_read = make_sql_read_tool("sales_sql_read","SELECT read access for sales/CRM domain tables")
sales_sql_write = make_sql_write_tool("sales_sql_write","INSERT write access for sales/CRM domain tables")
finance_sql_read = make_sql_read_tool("finance_sql_read","SELECT read access for finance domain tables")
finance_sql_write = make_sql_write_tool("finance_sql_write","INSERT write access for finance domain tables")
inventory_sql_read = make_sql_read_tool("inventory_sql_read","SELECT read access for inventory domain tables")
inventory_sql_write = make_sql_write_tool("inventory_sql_write","INSERT write access for inventory domain tables")
