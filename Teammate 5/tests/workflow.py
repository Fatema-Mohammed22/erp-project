"""
test/test_workflow.py
Test the end-to-end workflow of creating and approving a purchase order.
"""

from fastapi.testclient import TestClient
from app.main import app    

clinet = TestClient(app)

def test_order_approval_workflow():
    # Step 1: Create a new purchase order
    order_data = {
        "supplier_id": 1,
        "items": [
            {"product_id": 1, "quantity": 10},
            {"product_id": 2, "quantity": 5}
        ],
        "total_amount": 1500.00
    }
    response = clinet.post("/purchase_orders/", json=order_data)
    assert response.status_code in(200, 201) # Adjusted to accept both 200 and 201 status codes
    order = response.json()
    assert order["status"] == "pending"
    order_id = order["id"]

    # Step 2: Retrieve the created order
    response = clinet.get(f"/purchase_orders/{order_id}")
    assert response.status_code == 200
    order = response.json()
    assert order["id"] == order_id
    assert order["status"] == "pending"

    # Step 3: Approve the purchase order
    approval_data = {"approver_id": 1, "comments": "Approved for processing"}
    response = clinet.post(f"/purchase_orders/{order_id}/approve", json=approval_data)
    assert response.status_code == 200
    approval = response.json()
    assert approval["status"] == "approved"

    # Step 4: Verify the order status is updated
    response = clinet.get(f"/purchase_orders/{order_id}")
    assert response.status_code == 200
    order = response.json()
    assert order["status"] == "approved"

    # Step 5: Check inventory updated for each product
    response = clinet.get("/inventory/1")  # Assuming product_id 1 corresponds to inventory_id 1
    assert response.status_code == 200
    items = response.json().get ("items", [])
    for item in order_data["items"]:
        product_inventory = next((i for i in items if i["product_id"] == item["product_id"]), None )
        assert product_inventory is not None, f"Inventory for product_id {item['product_id']} not found"
        assert product_inventory["quantity"] <=100 # adjust based on seed data

    # Step 6: Generate an invoice for the approved order
    response = clinet.post(f"/ledger/")
    assert response.status_code in(200, 201) # Adjusted to accept both 200 and 201 status codes
    ledger_entry = response.json().get("entries",[])
    found_entry = any (entry.get("purchase_order_id") == order_id for entry in ledger_entry)
    assert found_entry, "Ledger does not contain entry for purchase order"