from src.db.db_init import orderdb, vectordb
from src.agents.orderAgent import OrderAgent
from src.agents.partAgent import PartAgent
from src.agents.troubleAgent import TroubleAgent

# Initialize agents once at module level (singleton pattern)
part_agent = PartAgent(vectordb)
order_agent = OrderAgent(orderdb)
trouble_agent = TroubleAgent(vectordb)

TOOL_ROUTES = {
    "search_parts": part_agent,
    "search_repairs": part_agent,
    "search_blogs": part_agent,
    "troubleshoot_issue": trouble_agent,
    "check_compatibility": part_agent,
    "get_installation_steps": part_agent,
    "place_order": order_agent,
    "check_order_status": order_agent,
    "cancel_order": order_agent,
}


async def handle_tool_call(function_name: str, arguments: dict):
    agent = TOOL_ROUTES.get(function_name)
    if not agent:
        return {"error": f"Unknown tool: {function_name}"}

    if not arguments:
        return {"error": "Missing arguments"}

    try:
        result = await agent.run(function_name, arguments)

        if not result:
            return {"message": "No results found"}

        return result
    except Exception as e:
        print(f"Tool execution error: {e}")
        return {"error": "Tool execution failed"}
