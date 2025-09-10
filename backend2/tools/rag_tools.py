from __future__ import annotations
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
from ..mcp.registry import MCPTool, global_registry
from pathlib import Path
import sqlite3, re, math, json
from collections import Counter
from ..memory.state import log_tool_call

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "erp.db"

def _load_docs():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        try:
            cur.execute("SELECT id, title, content FROM documents;")
            rows = [dict(r) for r in cur.fetchall()]
        except Exception:
            rows = []
    return rows

def _tokenize(text: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9_]+", (text or "").lower())

def _bm25_index(docs: List[Dict[str, Any]]):
    tokenized = [ _tokenize(d.get("title","") + " " + d.get("content","")) for d in docs ]
    df = Counter([tok for d in tokenized for tok in set(d)])
    avgdl = sum(len(d) for d in tokenized) / (len(tokenized) or 1)
    return {"docs": docs, "tok": tokenized, "df": df, "avgdl": avgdl, "N": len(docs)}

def _bm25_search(index, query: str, k: int = 5) -> List[Tuple[int, float]]:
    k1, b = 1.5, 0.75
    q_terms = _tokenize(query)
    scores = []
    for i, doc_terms in enumerate(index["tok"]):
        score = 0.0
        dl = len(doc_terms) or 1
        for q in q_terms:
            n_q = index["df"].get(q, 0)
            if n_q == 0:
                continue
            idf = math.log(1 + (index["N"] - n_q + 0.5) / (n_q + 0.5))
            f_q = doc_terms.count(q)
            denom = f_q + k1 * (1 - b + b * dl / index["avgdl"])
            if denom != 0:
                score += idf * (f_q * (k1 + 1)) / denom
        scores.append((i, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:k]

class RAGSearchParams(BaseModel):
    query: str = Field(description="Search string for local documents/glossary")
    k: int = Field(default=5, description="Top-k results")

def sales_rag_search_handler(model: RAGSearchParams):
    docs = _load_docs()
    idx = _bm25_index(docs)
    hits = _bm25_search(idx, model.query, k=model.k)
    res = []
    for i, score in hits:
        d = idx["docs"][i]
        res.append({"id": d.get("id"), "title": d.get("title"), "score": score, "snippet": (d.get("content","")[:200])})
    log_tool_call("sales_rag_search", model.json(), json.dumps({"hits": len(res)}), True)
    return res

sales_rag_search = MCPTool(
    name="sales_rag_search",
    description="Local BM25 search over documents table to support sales/CRM agent context",
    ParamModel=RAGSearchParams,
    handler=sales_rag_search_handler
)
global_registry.register(sales_rag_search)

class GlossaryParams(BaseModel):
    query: str
    k: int = 5

def rag_definition_tool_handler(model: GlossaryParams):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        try:
            cur.execute("SELECT term as title, definition as content FROM glossary;")
            g = [dict(r) for r in cur.fetchall()]
        except Exception:
            g = []
    if not g:
        return sales_rag_search_handler(RAGSearchParams(query=model.query, k=model.k))
    idx = _bm25_index(g)
    hits = _bm25_search(idx, model.query, k=model.k)
    res = [{"title": idx["docs"][i]["title"], "score": score, "snippet": idx["docs"][i]["content"][:200]} for i, score in hits]
    log_tool_call("rag_definition_tool", model.json(), json.dumps({"hits": len(res)}), True)
    return res

rag_definition_tool = MCPTool(
    name="rag_definition_tool",
    description="BM25 search over glossary for business definitions",
    ParamModel=GlossaryParams,
    handler=rag_definition_tool_handler
)
global_registry.register(rag_definition_tool)
