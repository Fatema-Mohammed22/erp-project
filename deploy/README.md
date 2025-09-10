# Agent-ERP Backend
FastAPI backend service for ERP-style workflows with **approvals** and **metadata queries**.  
Includes SQLite database, logging of tool calls, and Docker deployment.

---

## Features
- **Approvals API**
  - `/approvals/pending` → list pending approval requests
  - `/approvals/{id}/decide` → approve or reject a request
- **Meta API**
  - `/meta/tables` → list database tables
  - `/meta/query` → run read-only queries
- **Health Check**
  - `/health` → confirm API + DB connectivity
- **Logging**
  - Every call is logged into `tool_calls` table for auditing

---

## Project Structure
backend/
├─ main.py                   # FastAPI entrypoint
│
├─ routers/
│   ├─ approvals.py          # Approvals endpoints
│   └─meta.py                # Metadata endpoints
│
├─ utils/
│   ├─logger.py              # Logs tool calls into DB
│   └─db.py                  # DB helpers
│
├─ data/
│    └─ erp_sample.db        # Sample SQLit database
│
├─ deploy/
│   ├─Dockerfile             # Build instructions
│   ├─docker-compose.yml     # Run locally with Docker Compose
│   ├─requirements.txt       # Python dependencies
│   └─.env                   # Environment variables


---

## Sample Database

The project includes a ready-to-use SQLite database at `data/erp_sample.db`.  

### Example tables:
- `approvals`
- `customers`
- `invoices`
- `orders`
- `products`
- `tool_calls` (for logging)

### Example row in `approvals`:
```sql
SELECT * FROM approvals;

Results: 
| id | module  | payload\_json                                              | status   | requested\_by | decided\_by   | created\_at         |
| -- | ------- | ---------------------------------------------------------- | -------- | ------------- | ------------- | ------------------- |
| 1  | finance | {"action":"post\_invoice","invoice\_id":123,"amount":2500} | approved | user.alfa     | manager.bravo | 2025-09-03 10:53:47 |

Run Locally (Dev)

Install dependencies

pip install -r requirements.txt


Run with Uvicorn

uvicorn backend.main:app --reload


Open API docs

Swagger UI:http://127.0.0.1:8000/docs

Run with Docker

Build image

docker compose build


Run container

docker compose up -d


View logs

docker compose logs -f

Example API Calls
Get pending approvals
curl -X GET "http://127.0.0.1:8000/approvals/pending" -H "accept: application/json"

Decide an approval
curl -X POST "http://127.0.0.1:8000/approvals/1/decide" \
  -H "Content-Type: application/json" \
  -d '{"status": "approved", "decided_by": "manager.bravo"}'

List tables
curl -X GET "http://127.0.0.1:8000/meta/tables"

Run query
curl -X POST "http://127.0.0.1:8000/meta/query" \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT name FROM sqlite_master WHERE type='table';"}'

Notes

Only read-only SQL is allowed in /meta/query (INSERT, UPDATE, DELETE, etc. are blocked).

All calls are logged in tool_calls:

SELECT * FROM tool_calls;

