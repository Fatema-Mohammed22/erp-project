from __future__ import annotations
from typing import Any, Callable, Dict, Optional, List, Type
from pydantic import BaseModel, ValidationError

class MCPTool:
    name: str
    description: str
    ParamModel: Type[BaseModel]
    handler: Callable[[BaseModel], Any]

    def __init__(self, name: str, description: str, ParamModel: Type[BaseModel], handler: Callable[[BaseModel], Any]):
        self.name = name
        self.description = description
        self.ParamModel = ParamModel
        self.handler = handler

    def run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            model = self.ParamModel(**params)
        except ValidationError as e:
            return {"ok": False, "error": f"Parameter validation failed: {e.errors()}"}
        try:
            result = self.handler(model)
            return {"ok": True, "result": result}
        except Exception as e:
            return {"ok": False, "error": f"Tool execution failed: {e}"}

class MCPRegistry:
    def __init__(self):
        self._tools: Dict[str, MCPTool] = {}

    def register(self, tool: MCPTool):
        if tool.name in self._tools:
            raise ValueError(f"Tool {tool.name} already registered")
        self._tools[tool.name] = tool

    def list(self) -> List[Dict[str, Any]]:
        out = []
        for t in self._tools.values():
            out.append({
                "name": t.name,
                "description": t.description,
                "schema": t.ParamModel.model_json_schema()
            })
        return out

    def get(self, name: str) -> Optional[MCPTool]:
        return self._tools.get(name)

global_registry = MCPRegistry()
