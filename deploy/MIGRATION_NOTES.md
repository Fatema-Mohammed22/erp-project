# Migration & Developer Notes

This document is meant for developers extending or maintaining the **Agent-ERP Backend**.

---

## Database Setup

- The project uses **SQLite** by default (`data/erp_sample.db`).
- Schema is preloaded with common ERP-style tables:
  - `approvals`
  - `customers`, `orders`, `invoices`, `products`
  - `tool_calls` (logging)

### Reset Database
To reset to a fresh state:
```bash
rm -f data/erp_sample.db
python backend/scripts/seed_approval.py
Seeding Data
You can preload approvals or other data for testing.

Example: backend/scripts/seed_approval.py

python

from backend.db import execute

execute("""
INSERT INTO approvals (module, payload_json, requested_by)
VALUES ('finance', '{"action":"post_invoice","invoice_id":123,"amount":2500}', 'user.alfa')
""")
Run:

bash

python backend/scripts/seed_approval.py
Adding a New Router
Create a new file in backend/routers/
Example: inventory.py

Define an APIRouter:

python

from fastapi import APIRouter
from ..db import query_all
from backend.utils.logger import log_tool_call

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("/products")
def list_products():
    rows = query_all("SELECT * FROM products LIMIT 50;")
    log_tool_call("inventory", "list_products", "{}", f"{len(rows)} rows")
    return {"products": rows}
Register in backend/main.py:

python

from routers import inventory
app.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
Logging Behavior
All tool calls are stored in tool_calls.

Inserted automatically by log_tool_call() in each router.

Schema:

sql

CREATE TABLE tool_calls (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  agent TEXT,
  tool_name TEXT,
  input_json TEXT,
  output_json TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
Query logs:

sql
SELECT * FROM tool_calls ORDER BY created_at DESC LIMIT 10;
Deployment Notes
Local
Run with:

bash

uvicorn backend.main:app --reload
Docker
Build:

bash

docker compose build
Run:

bash

docker compose up -d
Logs:

bash
docker compose logs -f