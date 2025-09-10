"""
tests/test_tools.py
Test the tool execution endpoints.
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_tools():
    response = client.get("/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert isinstance(data["tools"], list)

def test_execute_known_tool():
    # Test executing a known tool with valid parameters
    payload = {
        "tool_name": "sales_sql_read",
        "params": {
            "sql": "SELECT name FROM sqlite_master WHERE type = 'table';"
        }
    }
    response = client.post("/tools/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data.get("ok") is True
    assert "result" in data

def test_execute_unknown_tool():
    # Test executing an unknown tool
    payload = {
        "tool_name": "unknown_tool",
        "params": {}
    }
    response = client.post("/tools/execute", json=payload)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Unknown tool unknown_tool"

def test_execute_tool_invalid_params():
    # Test executing a known tool with invalid parameters
    payload = {
        "tool_name": "sales_sql_read",
        "params": {
            "invalid_param": "value"
        }
    }
    response = client.post("/tools/execute", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data["detail"] 