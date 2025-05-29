def create_tool(name, description, properties, required):
    """Helper to create tool definitions"""
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
    }


# Core search tools
search_parts_tool = create_tool(
    "search_parts",
    "Search for appliance parts by ID, name, or description",
    {"query": {"type": "string", "description": "Part search query"}},
    ["query"]
)

search_repairs_tool = create_tool(
    "search_repairs",
    "Find repair guides for appliance problems",
    {
        "query": {"type": "string", "description": "Problem description"},
        "product": {"type": "string", "description": "Appliance type (optional)"}
    },
    ["query"]
)

search_blogs_tool = create_tool(
    "search_blogs",
    "Search maintenance articles and tips",
    {"query": {"type": "string", "description": "Search query"}},
    ["query"]
)

troubleshoot_issue_tool = create_tool(
    "troubleshoot_issue",
    "Find parts to fix specific issues",
    {"troubleshootText": {"type": "string", "description": "Issue description"}},
    ["troubleshootText"]
)

check_compatibility_tool = create_tool(
    "check_compatibility",
    "Check if a specific part ID is compatible with a specific model number. Use when customer asks 'Will part X work with model Y?' or 'Is part X compatible with model Y?'",
    {"modelList": {"type": "string", "description": "Query containing both part ID and model number, e.g. 'Will PS11745480 work with model 66513402K900?'"}},
    ["modelList"]
)

get_installation_steps_tool = create_tool(
    "get_installation_steps",
    "Get installation instructions",
    {"part_id": {"type": "string", "description": "Part ID"}},
    ["part_id"]
)

# Order management tools
place_order_tool = create_tool(
    "place_order",
    "Create order for parts",
    {
        "user_id": {"type": "string", "description": "User ID"},
        "items": {"type": "array", "description": "List of [part_id, quantity] pairs"},
        "total_amount": {"type": "number", "description": "Total amount"}
    },
    ["user_id", "items", "total_amount"]
)

check_order_status_tool = create_tool(
    "check_order_status",
    "Check order status",
    {"order_id": {"type": "string", "description": "Order ID"}},
    ["order_id"]
)

cancel_order_tool = create_tool(
    "cancel_order",
    "Cancel an order",
    {"order_id": {"type": "string", "description": "Order ID"}},
    ["order_id"]
)

# All available tools
ALL_TOOLS = [
    search_parts_tool,
    search_repairs_tool,
    search_blogs_tool,
    troubleshoot_issue_tool,
    check_compatibility_tool,
    get_installation_steps_tool,
    place_order_tool,
    check_order_status_tool,
    cancel_order_tool,
]
