import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from src.services.mcp import ALL_TOOLS
load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")


class LLM:
    def __init__(self):
        if not DEEPSEEK_API_KEY:
            raise ValueError("Missing API key")

        self.client = AsyncOpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com/v1",
            timeout=30.0,
            max_retries=2
        )

    async def ask_llm(self, messages: list[dict], model: str = "deepseek-chat") -> str:
        try:
            domain_guardrail = {
                "role": "system",
                "content": (
                    "You help with refrigerator & dishwasher parts, repairs, and orders only.\n"
                    "AVAILABLE TOOLS: search_parts, search_repairs, search_blogs, troubleshoot_issue, "
                    "check_compatibility, get_installation_steps, place_order, check_order_status, cancel_order\n\n"
                    "TOOL SELECTION RULES:\n"
                    "For troubleshooting/diagnosing problems (words like 'troubleshoot', 'not working', 'broken', 'problem with', 'issue with') → troubleshoot_issue\n"
                    "For finding specific parts by name/ID → search_parts\n"
                    "For repair guides → search_repairs\n"
                    "For compatibility questions → check_compatibility\n"
                    "For order management → place_order, check_order_status, cancel_order\n\n"
                    "IMPORTANT: If user asks to troubleshoot, diagnose, or fix a problem, ALWAYS use troubleshoot_issue tool, not search_parts.\n"
                    "Reject unrelated requests: 'I only help with refrigerator and dishwasher parts, repairs, and orders.'"
                )
            }

            all_messages = [domain_guardrail] + messages

            response = await self.client.chat.completions.create(
                model=model,
                messages=all_messages,
                tools=ALL_TOOLS,
                tool_choice="auto",
                max_tokens=500,
                temperature=0.0,
                stream=False,
                top_p=0.9
            )

            return response

        except Exception as e:
            print(f"LLM Error: {e}")
            error_message = "I'm currently experiencing technical difficulties. Please try again later."
            return type('Response', (), {
                'choices': [
                    type('Choice', (), {
                        'message': type('Message', (), {
                            'content': error_message,
                            'tool_calls': None
                        })
                    })
                ]
            })
