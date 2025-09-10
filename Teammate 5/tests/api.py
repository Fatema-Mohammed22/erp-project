"""
tests/test_api.py
Test all FastAPI endpoints from the ERP backend.
"""

from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)

#----------------------
# Customers
#----------------------
def test_get_customer():
    response = client.get("/customers/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "name" in data
    assert "email" in data
    assert "phone" in data
    assert "created_at" in data

#----------------------
# Suppliers
#----------------------
def test_get_supplier():
    response = client.get("/suppliers/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "name" in data
    assert "email" in data
    assert "phone" in data

#----------------------
# Products
#----------------------
def test_get_product():
    response = client.get("/products/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "sku" in data
    assert "name" in data
    assert "price" in data
    assert "description" in data

#----------------------
# Orders
#----------------------
def test_create_order():
    response = client.get("/orders/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "customer_id" in data
    assert "total" in data
    assert "status" in data
    assert "created_at" in data

#----------------------
# Invoices
#----------------------
def test_generate_invoice():
    response = client.get("/invoices/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "customer_id" in data
    assert "invoice_number" in data
    assert "issue_date" in data
    assert "due_date" in data
    assert "total_amount" in data
    assert "status" in data
    assert "created_at" in data

#----------------------
# Inventory
#----------------------
def test_get_inventory():
    response = client.get("/inventory/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "product_id" in data
    assert "quantity" in data
    assert "location" in data
    assert "last_updated" in data

#----------------------
# Ledger
#----------------------
def test_get_ledger_entry():
    response = client.get("/ledger/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "entry_type" in data
    assert "created_at" in data

#----------------------
# Glossary 
#----------------------
def test_get_glossary_term():
    response = client.get("/glossary/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "term" in data
    assert "definition" in data 
    assert "module" in data

#----------------------
# Approvals
#----------------------
def test_get_approval():
    response = client.get("/approvals/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "module" in data
    assert "pyload_json" in data
    assert "status" in data
    assert "requested_by" in data
    assert "decided_by" in data
    assert "created_at" in data
    assert "decided_at" in data

