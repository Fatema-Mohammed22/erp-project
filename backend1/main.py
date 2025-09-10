from fastapi import FastAPI
from .routers import meta, approvals

app = FastAPI(title="Agent-ERP Backend", version="0.1")

# Root + health
@app.get("/")
def root():
    return {"msg": "Agent-ERP backend is running"}

@app.get("/health")
def health():
    return {"status": "ok", "db": "connected"}

# Attach routers
app.include_router(meta.router)
app.include_router(approvals.router)



