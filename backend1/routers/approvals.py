from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..db import query_all, execute
from ..utils.logger import log_tool_call  

router = APIRouter(prefix="/approvals", tags=["approvals"])

@router.get("/pending")
def pending():
    rows = query_all("""
      SELECT id, module, payload_json, status, requested_by, created_at
      FROM approvals
      WHERE status='pending'
      ORDER BY created_at DESC;
    """)

    # ✅ log tool call
    log_tool_call("approvals", "pending", "{}", str(rows))

    return {"pending": rows}


class DecisionIn(BaseModel):
    status: str  # "approved" or "rejected"
    decided_by: str

@router.post("/{approval_id}/decide")
def decide(approval_id: int, body: DecisionIn):
    if body.status not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="status must be approved or rejected")
    try:
        execute(
            "UPDATE approvals SET status=?, decided_by=?, decided_at=datetime('now') WHERE id=?;",
            (body.status, body.decided_by, approval_id),
        )

        # ✅ log tool call
        log_tool_call("approvals", "decide", f"id={approval_id}, body={body.json()}", body.status)

        return {"approval_id": approval_id, "status": body.status}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

