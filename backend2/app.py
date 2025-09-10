from __future__ import annotations
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from .mcp.registry import global_registry
from .memory.state import init_memory_tables

# registration side-effects
from .tools import sql_tools, rag_tools, ml_tools  # noqa: F401

app = FastAPI(title="Agent ERP MCP Tool Server")

class ExecRequest(BaseModel):
    tool_name: str
    params: Dict[str, Any] = {}

@app.on_event("startup")
def on_startup():
    init_memory_tables()

@app.get("/tools")
def list_tools():
    return {"tools": global_registry.list()}

@app.post("/tools/execute")
def execute_tool(req: ExecRequest):
    tool = global_registry.get(req.tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Unknown tool {req.tool_name}")
    result = tool.run(req.params)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result
