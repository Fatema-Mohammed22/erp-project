from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..db import query_all
from ..utils.logger import log_tool_call   # ✅ keep this

router = APIRouter(prefix="/meta", tags=["meta"])

@router.get("/tables")
def list_tables():
    rows = query_all("""
      SELECT name, sql
      FROM sqlite_master
      WHERE type='table' AND name NOT LIKE 'sqlite_%'
      ORDER BY name;
    """)
    
    # ✅ log the tool call
    log_tool_call("meta", "list_tables", "{}", str(rows))

    return {"tables": rows}


class QueryIn(BaseModel):
    sql: str

@router.post("/query")
def run_query(payload: QueryIn):
    sql = payload.sql.strip().lower()
    forbidden = ("insert ", "update ", "delete ", "drop ", "alter ", "create ")
    if any(sql.startswith(x) for x in forbidden):
        raise HTTPException(status_code=400, detail="Write/DDL statements are not allowed on this endpoint.")
    try:
        data = query_all(payload.sql)

        # ✅ log the tool call
        log_tool_call("meta", "run_query", payload.sql, str(data))

        return {"rows": data, "rowcount": len(data)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
