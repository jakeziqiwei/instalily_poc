from src.services.llm import LLM


class PartAgent:
    def __init__(self, vectordb):
        self.vectordb = vectordb

    def _no_results_message(self, tool_name):
        """Generate appropriate no results message based on tool"""
        messages = {
            "search_parts": "No parts found. Try a different search term or part ID.",
            "search_repairs": "No repair guides found. Try searching for specific parts instead.",
            "search_blogs": "No articles found. Try a different search term.",
            "check_compatibility": "No compatible parts found. Please verify the model number.",
            "get_installation_steps": "Installation instructions not found. Please verify the part ID."
        }
        return {"message": messages.get(tool_name, "No results found.")}

    def search_parts(self, query):
        """Search for parts with fallback to related parts"""
        result = self.vectordb.search_parts(query)
        parts = result.get('data', {}).get(
            'Get', {}).get('Part', []) if result else []

        if parts:
            return result

        # No results found, provide helpful fallback message
        if len(query) > 5 and any(char.isdigit() for char in query):
            return {
                "message": f"I couldn't find part '{query}' in our database. Please check the part number or try describing what part you need (like 'dishwasher door seal' or 'refrigerator water filter')."
            }

        return {"message": f"No parts found for '{query}'. Try a different search term."}

    def check_compatibility(self, model_list):
        """Check compatibility between part ID and model number"""
        words = model_list.split()
        part_id = None
        model_number = None

        # Look for part ID patterns (PS, WP, W10 followed by numbers)
        for word in words:
            clean_word = word.rstrip('.,!?;:')  # Strip punctuation

            if len(clean_word) > 5 and clean_word.upper().startswith(('PS', 'WP', 'W10')):
                part_id = clean_word
            elif len(clean_word) > 5 and any(char.isdigit() for char in clean_word) and any(char.isalpha() for char in clean_word):
                model_number = clean_word

        # If we have both part ID and model number, do specific compatibility check
        if part_id and model_number:
            result = self.vectordb.check_part_compatibility(
                part_id, model_number)
            if result:
                return result

        # Fall back to finding parts for this model
        return self.vectordb.find_compatible_parts(model_list)

    async def run(self, function_name: str, data: dict):
        """Handle all part-related operations"""
        handlers = {
            "search_parts": lambda: self.search_parts(data["query"]),
            "search_repairs": lambda: self.vectordb.search_repairs(data["query"], data.get("product")),
            "search_blogs": lambda: self.vectordb.search_blogs(data["query"]),
            "check_compatibility": lambda: self.check_compatibility(data["modelList"]),
            "get_installation_steps": lambda: self.vectordb.get_part_by_id(data["part_id"])
        }

        handler = handlers.get(function_name)
        if not handler:
            return {"message": "Unknown function"}

        result = handler()

        # Special handling for compatibility checks that return structured results
        if function_name == "check_compatibility" and isinstance(result, dict):
            if 'compatible' in result or "message" in result:
                return result

        # Handle custom messages (like our fallback messages)
        if isinstance(result, dict) and "message" in result:
            return result

        # Check if we got valid results
        if not result or not result.get('data', {}).get('Get'):
            return self._no_results_message(function_name)

        collections = result['data']['Get']
        if not any(collections.get(col) for col in ['Part', 'Repair', 'Blog']):
            return self._no_results_message(function_name)

        return result
