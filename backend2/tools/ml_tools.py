from __future__ import annotations
from typing import Dict, Any
from pydantic import BaseModel, Field
from ..mcp.registry import MCPTool, global_registry
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import IsolationForest
import numpy as np, json
from pathlib import Path
from ..memory.state import log_tool_call

MODEL_DIR = Path(__file__).resolve().parents[2] / "data" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

class LeadScoreParams(BaseModel):
    email_length: int = Field(ge=0)
    has_keywords: int = Field(ge=0, le=1, description="1 if message contains purchase intent keywords")
    visits_last_30d: int = Field(ge=0)

def _get_lead_model():
    X = []
    y = []
    for L in range(10, 400, 20):
        for kw in [0,1]:
            for v in [0,1,2,3,4,5,10]:
                X.append([L, kw, v])
                y.append(1 if (kw==1 and v>=2) or (L>200 and kw==1) else 0)
    X = np.array(X); y = np.array(y)
    model = LogisticRegression(max_iter=1000).fit(X,y)
    model.classes_ = np.array([0,1])
    return model

def lead_score_handler(p: LeadScoreParams):
    model = _get_lead_model()
    X = np.array([[p.email_length, p.has_keywords, p.visits_last_30d]])
    prob = float(model.predict_proba(X)[0,1])
    score = int(round(prob*100))
    res = {"lead_score": score, "probability": prob}
    log_tool_call("lead_score_tool", p.json(), json.dumps(res), True)
    return res

lead_score_tool = MCPTool(
    name="lead_score_tool",
    description="Predict a lead score (0-100) from simple features",
    ParamModel=LeadScoreParams,
    handler=lead_score_handler
)
global_registry.register(lead_score_tool)

class AnomalyParams(BaseModel):
    amount: float
    vendor_freq: int
    day_of_month: int

def _get_iforest():
    rng = np.random.default_rng(0)
    X = np.vstack([
        np.column_stack([rng.normal(500, 80, 500), rng.integers(1,30,500), rng.integers(1,28,500)]),
        np.column_stack([rng.normal(5000, 200, 20), rng.integers(1,30,20), rng.integers(1,28,20)])
    ])
    m = IsolationForest(random_state=0, contamination=0.05).fit(X)
    return m

def anomaly_handler(p: AnomalyParams):
    model = _get_iforest()
    X = np.array([[p.amount, p.vendor_freq, p.day_of_month]])
    score = float(-model.score_samples(X)[0])
    flagged = score > 0.6
    res = {"anomaly_score": score, "flagged": bool(flagged)}
    log_tool_call("anomaly_detector_tool", p.json(), json.dumps(res), True)
    return res

anomaly_detector_tool = MCPTool(
    name="anomaly_detector_tool",
    description="IsolationForest-based anomaly detector for invoices",
    ParamModel=AnomalyParams,
    handler=anomaly_handler
)
global_registry.register(anomaly_detector_tool)
