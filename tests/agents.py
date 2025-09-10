"""
test/ test_agents.py
covers Router Agents, Sales/CRM, Finance, and Inventory agents.
"""
from agents.router_agent import RouterAgent
from agents.sales_agent import SalesAgent
from agents.finance_agent import FinanceAgent
from agents.inventory_agent import InventoryAgent
import pytest

# initialize agents
router_agent = RouterAgent()
sales_agent = SalesAgent()
finance_agent = FinanceAgent()
inventory_agent = InventoryAgent()

#----------------------
# 1. Test Router Agent Intent Routing 
#-----------------------
def test_router_routing_sales_order():
    query = "Create a sales order for customer ID 1 with product ID 2, quantity 3."
    response = router_agent.handle_query(query)
    # Router should detect 'sales' intent 
    assert response["agent"] == "sales"
    #And return order info or confirmation
    assert "order_id" in response 
    assert response["status"] in ("created", "pending")

#----------------------
# 2. Test Sales/CRM Workflow
#-----------------------
def test_sales_agent_full_flow():
    # Place order
    order = sales_agent.place_order(customer_id=1, product_id=2, qty=3)
    order_id = order["order_id"]
    # Approve order
    approval = sales_agent.approve_order(order_id=order_id, approver_id=1)
    assert approval["status"] == "approved"
    # Verify order retrieval
    fetched = sales_agent.get_order(order_id=order_id)
    assert fetched["status"] == "approved"

#----------------------
# 3. Test Finance Agent (Invoice & Ledger) 
# ----------------------
def test_finance_agent_invoice_generation(): 
    # Generate invoice for order
    invoice = finance_agent.generate_invoice(order_id=1)
    assert "invoice_id" in invoice
    assert invoice["total_amount"] > 0
    # Verify ledger entry creation
    ledger_entry = finance_agent.create_ledger_entry(invoice_id=invoice["invoice_id"], entry_type="debit")
    assert "entry_id" in ledger_entry

#----------------------
# 4. Test Inventory Agent (Stock Check + supplier lookup)
#----------------------
def test_inventory_agent_stock_check_and_supplier_lookup():
    # Check stock for product
    stock = inventory_agent.check_stock(product_id=2)
    assert "quantity" in stock
    assert stock["quantity"] >= 0
    # Lookup supplier info
    supplier = inventory_agent.lookup_supplier(supplier_id=1)
    assert "name" in supplier
    assert "contact" in supplier

#----------------------
# 5. Test Router + Multi-Agent Workflow
#----------------------
def test_router_full_workflow():
    query = "customer 1 wants to order 5 units of product 2"
    response = router_agent.handle_query(query)

    # Router delegates to Sales Agent
    assert response["agent"] == "sales"
    order_id = response["order_id"]
    
    # Fiance agent generates invoice 
    invoice = finance_agent.generate_invoice(order_id=order_id)
    assert "invoice_id" in invoice

    # Inventory agent checks stock
    stock = inventory_agent.check_stock(product_id=2)
    assert stock >= 0 # ensure stock is non-negative

    # Router enforces aproval
    approval_response = router_agent.handle_query(f"Approve order {order_id} by approver 1")
    assert approval_response["status"] == "approved"
