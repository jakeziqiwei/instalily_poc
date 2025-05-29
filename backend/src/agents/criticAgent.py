from src.services.llm import LLM
from src.services.cache import SimpleCache


class CriticAgent:
    def __init__(self):
        self.llm = LLM()
        self.cache = SimpleCache()

    async def run(self, response_text: str, instructions: str = "") -> str:
        """Format responses to be friendly and helpful with caching"""

        cache_key = self.cache._generate_key(response_text, instructions)

        cached_response = self.cache.get(cache_key)
        if cached_response:
            return cached_response

        # Check if response is a troubleshooting response that needs special formatting
        if self._is_troubleshooting_response(response_text):
            formatted_response = await self._format_troubleshooting_response(response_text)
            self.cache.set(cache_key, formatted_response)
            return formatted_response

        prompt = {
            "role": "system",
            "content": (
                "Format responses to be friendly and helpful for appliance parts customers.\n\n"
                "Rules:\n"
                "- Start with a warm greeting\n"
                "- Present information clearly\n"
                "- Use encouraging language\n"
                "- End with helpful next steps\n"
                "- Never use meta-labels like 'human friendly response'\n\n"
                "For compatibility checks:\n"
                "- If compatible=True: Start with 'Yes!' and explain why it works\n"
                "- If compatible=False: Start with 'No,' and explain why it doesn't work\n"
                "- Always mention the part name and model number clearly\n"
                "- If not compatible, suggest next steps (check model number, contact support)\n\n"
                "When we don't have the exact part but have recommendations:\n"
                "- Acknowledge we couldn't find the exact part\n"
                "- Present the recommended parts as helpful alternatives\n"
                "- Encourage the customer to check if these might work\n\n"
                "Format parts as:\n"
                "**[Part Name] ([Part ID])**\n"
                "**Brand:** [Brand] | **Price:** [Price] | **Status:** [Availability]\n"
                "**About:** [Description]\n"
                "**Links:** [Installation Video] | [Product Page]\n\n"
                "Format repairs as:\n"
                "**[Symptom]**\n"
                "**Description:** [Description]\n"
                "**Difficulty:** [Difficulty] | **Parts Needed:** [Parts]\n"
                "**Repair Video:** [repairVideoUrl] | **Detailed Guide:** [symptomDetailUrl]\n\n"
                "Always include repair video links and detailed guide URLs when available.\n\n"
                "End with: 'Need help with compatibility or ordering? Just ask!'"
            )
        }

        messages = [prompt, {"role": "user",
                             "content": f"{response_text}"}]

        try:
            result = await self.llm.ask_llm(messages)
            if hasattr(result, 'choices') and result.choices:
                formatted_response = result.choices[0].message.content
                self.cache.set(cache_key, formatted_response)
                return formatted_response
        except Exception as e:
            print(f"Critic Agent Error: {e}")

        return response_text

    def _is_troubleshooting_response(self, response_text: str) -> bool:
        """Check if response is a troubleshooting response from TroubleAgent"""
        troubleshooting_indicators = [
            "TROUBLESHOOTING_ISSUE:",
            "POTENTIAL_STEPS:",
            "REPAIR_GUIDES:",
            "RECOMMENDED_PARTS:",
            "HELPFUL_RESOURCES:"
        ]

        # If response contains troubleshooting structure, format it specially
        return any(indicator in response_text for indicator in troubleshooting_indicators)

    async def _format_troubleshooting_response(self, response_text: str) -> str:
        """Format troubleshooting responses into user-friendly format"""

        # Always use fallback formatting for now since LLM formatting is failing
        return self._fallback_format_troubleshooting(response_text)

        # Commenting out LLM formatting for now - can be re-enabled later
        # prompt = {
        #     "role": "system",
        #     "content": (
        #         "You are formatting a troubleshooting response for appliance customers. "
        #         "Create a friendly, helpful response that guides them through the troubleshooting process.\n\n"
        #         "Format Guidelines:\n"
        #         "- Start with a warm, encouraging greeting\n"
        #         "- Present the troubleshooting steps clearly and in order\n"
        #         "- Format repair guides as numbered or bulleted lists\n"
        #         "- Present parts information attractively with prices and links\n"
        #         "- Include helpful resources at the end\n"
        #         "- Use encouraging language throughout\n"
        #         "- End with an offer to help further\n\n"
        #         "Structure your response as:\n"
        #         "1. Friendly greeting acknowledging their issue\n"
        #         "2. Clear troubleshooting steps to try\n"
        #         "3. Repair guides if available\n"
        #         "4. Recommended parts with details\n"
        #         "5. Additional helpful resources\n"
        #         "6. Encouraging closing with offer to help\n\n"
        #         "Make it feel like getting help from a knowledgeable, friendly technician."
        #     )
        # }

        # user_message = {
        #     "role": "user",
        #     "content": f"Please format this troubleshooting information into a friendly, helpful response:\n\n{response_text}"
        # }

        # try:
        #     result = await self.llm.ask_llm([prompt, user_message])
        #     if hasattr(result, 'choices') and result.choices:
        #         return result.choices[0].message.content
        #     else:
        #         return self._fallback_format_troubleshooting(response_text)
        # except Exception as e:
        #     print(f"Error formatting troubleshooting response: {e}")
        #     return self._fallback_format_troubleshooting(response_text)

    def _fallback_format_troubleshooting(self, response_text: str) -> str:
        """Fallback formatting if LLM fails"""
        lines = response_text.split('\n')
        formatted_lines = []

        current_section = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("TROUBLESHOOTING_ISSUE:"):
                issue = line.replace("TROUBLESHOOTING_ISSUE:", "").strip()
                formatted_lines.append(
                    f"I can help you troubleshoot: **{issue}**\n")

            elif line.startswith("POTENTIAL_STEPS:"):
                formatted_lines.append(
                    "## 🔧 Let's try these troubleshooting steps:")
                current_section = "steps"

            elif line.startswith("REPAIR_GUIDES:"):
                formatted_lines.append("\n## 📋 Repair Guides:")
                current_section = "guides"

            elif line.startswith("RECOMMENDED_PARTS:"):
                formatted_lines.append("\n## 🔧 Parts You Might Need:")
                current_section = "parts"

            elif line.startswith("HELPFUL_RESOURCES:"):
                formatted_lines.append("\n## 📚 Helpful Resources:")
                current_section = "resources"

            else:
                # Format content based on current section
                if current_section == "steps" and line.startswith(("1.", "2.", "3.", "4.", "5.")):
                    formatted_lines.append(f"**{line}**")
                elif line.startswith("-"):
                    formatted_lines.append(line)
                else:
                    formatted_lines.append(line)

        formatted_lines.append(
            "\n💡 **Need more help?** Feel free to ask about specific parts or if you need clarification on any of these steps!")

        return "\n".join(formatted_lines)
