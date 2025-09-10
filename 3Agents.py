import sys
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel
from langchain.agents import create_react_agent, AgentExecutor
from langchain.schema import HumanMessage

# Allow imports from parent folder if needed
sys.path.insert(0, str(Path(__file__).parent.parent))

# adjust this import to the real path of your sql tools file
from tools.sql_tools import (
    sales_sql_read, sales_sql_write,
    finance_sql_read, finance_sql_write,
    inventory_sql_read, inventory_sql_write
)

# ---------- LLM ----------
from config.llm import get_llm
from config.prompts import get_react_prompt

def get_llm():
    return ChatOpenAI(
        openai_api_key="API Key", 
        model_name="gpt-4o",
        temperature=0
    )

    )
# ---------- SALES AGENT ----------
SALES_TOOLS = [sales_sql_read, sales_sql_write]
SALES_SYSTEM = """You are a Sales Agent specialized in CRM and sales operations.
You can run SELECT queries with sales_sql_read and insert rows with sales_sql_write.
Use only the allowed tables. Never run non-SELECT queries with *_sql_read."""
sales_prompt = get_react_prompt(system_prompt=SALES_SYSTEM)
sales_agent = create_react_agent(llm=llm, tools=SALES_TOOLS, prompt=sales_prompt)
sales_executor = AgentExecutor(agent=sales_agent)

# ---------- FINANCE AGENT ----------
FINANCE_TOOLS = [finance_sql_read, finance_sql_write]
FINANCE_SYSTEM = """You are a Finance Agent specialized in financial operations.
You can run SELECT queries with finance_sql_read and insert rows with finance_sql_write.
Use only the allowed tables. Never run non-SELECT queries with *_sql_read."""
finance_prompt = get_react_prompt(system_prompt=FINANCE_SYSTEM)
finance_agent = create_react_agent(llm=llm, tools=FINANCE_TOOLS, prompt=finance_prompt)
finance_executor = AgentExecutor(agent=finance_agent)

# ---------- INVENTORY AGENT ----------
INVENTORY_TOOLS = [inventory_sql_read, inventory_sql_write]
INVENTORY_SYSTEM = """You are an Inventory Agent specialized in inventory management.
You can run SELECT queries with inventory_sql_read and insert rows with inventory_sql_write.
Use only the allowed tables. Never run non-SELECT queries with *_sql_read."""
inventory_prompt = get_react_prompt(system_prompt=INVENTORY_SYSTEM)
inventory_agent = create_react_agent(llm=llm, tools=INVENTORY_TOOLS, prompt=inventory_prompt)
inventory_executor = AgentExecutor(agent=inventory_agent)

# ---------- ROUTER ----------
class RouterAgent:
    def __init__(self, llm, sales_exec, finance_exec, inventory_exec):
        self.llm = llm
        self.sales_exec = sales_exec
        self.finance_exec = finance_exec
        self.inventory_exec = inventory_exec

    def route(self, user_input: str) -> str:
        router_prompt = f"""
        You are an ERP router. Decide which agent should handle the request:
        SalesAgent, FinanceAgent or InventoryAgent.
        Only respond with one of those names.
        User request: "{user_input}"
        """
        decision = self.llm([HumanMessage(content=router_prompt)]).content.strip()
        if decision == "SalesAgent":
            return self.sales_exec.run(user_input)
        elif decision == "FinanceAgent":
            return self.finance_exec.run(user_input)
        elif decision == "InventoryAgent":
            return self.inventory_exec.run(user_input)
        else:
            return "Router: could not determine appropriate agent."

router = RouterAgent(llm, sales_executor, finance_executor, inventory_executor)

# ---------- FASTAPI ----------
app = FastAPI()

class Query(BaseModel):
    text: str

@app.post("/query")
def query_endpoint(q: Query):
    reply = router.route(q.text)
    return {"response": reply}

