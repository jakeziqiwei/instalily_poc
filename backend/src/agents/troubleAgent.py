from src.services.llm import LLM
from src.services.cache import SimpleCache


class TroubleAgent:
    def __init__(self, vectordb):
        self.vectordb = vectordb
        self.llm = LLM()
        self.cache = SimpleCache()

    async def run(self, function_name: str, data: dict):
        """Handle troubleshooting requests by providing steps and resources"""
        try:
            # Extract the troubleshoot text from the data
            query = data.get("troubleshootText", "")
            if not query:
                return {"message": "No troubleshooting text provided"}

            # Check cache first
            cache_key = self.cache._generate_key("troubleshoot", query)
        cached_response = self.cache.get(cache_key)
        if cached_response:
            return cached_response

            # Search across all data sources
            repairs_data = self.vectordb.search_repairs(query, limit=3)
            parts_data = self.vectordb.search_parts(query, limit=5)
            blogs_data = self.vectordb.search_blogs(query, limit=3)

            # Extract relevant information
            repairs = repairs_data.get('data', {}).get(
                'Get', {}).get('Repair', []) if repairs_data else []
            parts = parts_data.get('data', {}).get(
                'Get', {}).get('Part', []) if parts_data else []
            blogs = blogs_data.get('data', {}).get(
                'Get', {}).get('Blog', []) if blogs_data else []

            # If no data found, return helpful message
            if not repairs and not parts and not blogs:
                return {"message": f"No troubleshooting information found for: {query}. Try describing the problem differently or be more specific about the symptoms."}

            # Generate troubleshooting guidance
            troubleshooting_info = self._generate_troubleshooting_guidance(
                query, repairs, parts, blogs)

            # Cache the result
            self.cache.set(cache_key, troubleshooting_info)

            return troubleshooting_info

        except Exception as e:
            print(f"Trouble Agent Error: {e}")
            return {"message": "Error processing troubleshooting request"}

    def _generate_troubleshooting_guidance(self, query, repairs, parts, blogs):
        """Generate structured troubleshooting guidance with steps and resources"""

        # Start building the response
        response = {
            "troubleshooting_issue": query,
            "potential_steps": [],
            "recommended_parts": [],
            "helpful_resources": [],
            "repair_guides": []
        }

        # Add repair-based troubleshooting steps
        for repair in repairs:
            if repair.get('symptom') and repair.get('description'):
                step_info = {
                    "symptom": repair.get('symptom'),
                    "description": repair.get('description'),
                    "difficulty": repair.get('difficulty', 'Unknown'),
                    "parts_needed": repair.get('parts', ''),
                    "video_url": repair.get('repairVideoUrl', '')
                }
                response["repair_guides"].append(step_info)

        # Add recommended parts
        for part in parts:
            if part.get('partName') and part.get('partId'):
                part_info = {
                    "name": part.get('partName'),
                    "id": part.get('partId'),
                    "price": part.get('price', 0),
                    "brand": part.get('brand', ''),
                    "description": part.get('productDescription', ''),
                    "video_url": part.get('youtubeVideoUrl', ''),
                    "product_url": part.get('productUrl', ''),
                    "availability": part.get('availability', 'Unknown')
                }
                response["recommended_parts"].append(part_info)

        # Add helpful blog resources
        for blog in blogs:
            if blog.get('title') and blog.get('url'):
                blog_info = {
                    "title": blog.get('title'),
                    "url": blog.get('url'),
                    "category": blog.get('category', '')
                }
                response["helpful_resources"].append(blog_info)

        # Generate general troubleshooting steps based on the issue
        response["potential_steps"] = self._generate_general_steps(
            query, repairs)

        # Create a formatted message for the CriticAgent to work with
        message = self._format_for_critic_agent(response)

        return {"message": message, "troubleshooting_data": response}

    def _generate_general_steps(self, query, repairs):
        """Generate general troubleshooting steps based on the issue"""
        steps = []

        # Common steps based on keywords in the query
        if "not draining" in query.lower() or "standing water" in query.lower():
            steps = [
                "Check for clogs in the drain hose",
                "Inspect the garbage disposal if connected",
                "Clean the dishwasher filter",
                "Test the drain pump motor",
                "Verify proper installation of drain hose"
            ]
        elif "not cleaning" in query.lower() or "dirty dishes" in query.lower():
            steps = [
                "Check water temperature (should be 120°F)",
                "Clean spray arms for blockages",
                "Verify proper loading of dishes",
                "Check detergent dispenser",
                "Inspect wash pump motor"
            ]
        elif "noise" in query.lower() or "grinding" in query.lower():
            steps = [
                "Check for debris in spray arms",
                "Inspect wash pump motor",
                "Verify dishwasher is level",
                "Check for loose connections",
                "Examine door seals and gaskets"
            ]
        elif "not filling" in query.lower():
            steps = [
                "Check water supply valve",
                "Test water inlet valve",
                "Inspect door latch and switches",
                "Verify adequate water pressure",
                "Check for kinked fill hose"
            ]
        else:
            # Generic steps from repair data if available
            if repairs:
                steps = [
                    f"Check: {repair.get('description', '')}" for repair in repairs[:3]]
            else:
                steps = [
                    "Check power supply and connections",
                    "Inspect for visible damage or wear",
                    "Verify proper operation of related components",
                    "Consult manufacturer's troubleshooting guide"
                ]

        return steps

    def _format_for_critic_agent(self, response_data):
        """Format the troubleshooting data for the CriticAgent to process"""
        message_parts = []

        # Add issue description
        message_parts.append(
            f"TROUBLESHOOTING_ISSUE: {response_data['troubleshooting_issue']}")

        # Add potential steps
        if response_data['potential_steps']:
            message_parts.append("POTENTIAL_STEPS:")
            for i, step in enumerate(response_data['potential_steps'], 1):
                message_parts.append(f"{i}. {step}")

        # Add repair guides
        if response_data['repair_guides']:
            message_parts.append("REPAIR_GUIDES:")
            for guide in response_data['repair_guides']:
                message_parts.append(
                    f"- {guide['symptom']}: {guide['description']} (Difficulty: {guide['difficulty']})")
                if guide['video_url']:
                    message_parts.append(f"  Video: {guide['video_url']}")

        # Add recommended parts
        if response_data['recommended_parts']:
            message_parts.append("RECOMMENDED_PARTS:")
            for part in response_data['recommended_parts']:
                message_parts.append(
                    f"- {part['name']} ({part['id']}) - ${part['price']} by {part['brand']}")
                if part['video_url']:
                    message_parts.append(
                        f"  Installation Video: {part['video_url']}")

        # Add helpful resources
        if response_data['helpful_resources']:
            message_parts.append("HELPFUL_RESOURCES:")
            for resource in response_data['helpful_resources']:
                message_parts.append(
                    f"- {resource['title']}: {resource['url']}")

        return "\n".join(message_parts)
