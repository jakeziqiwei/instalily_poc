import os
import weaviate
from weaviate.classes.init import Auth, AdditionalConfig, Timeout
from weaviate.classes.config import Configure, DataType, Property
from weaviate.classes.query import Filter, MetadataQuery
from dotenv import load_dotenv
from src.services.cache import SimpleCache

load_dotenv()

# Best practice: store your credentials in environment variables
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")

if not WEAVIATE_URL or not WEAVIATE_API_KEY:
    raise ValueError(
        "WEAVIATE_URL and WEAVIATE_API_KEY environment variables must be set")


class VectorDB:
    def __init__(self):
        self.weaviate_url = os.getenv("WEAVIATE_URL")
        self.weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
        self.client = None
        self.cache = SimpleCache(ttl=300)

        self._connect()
        if self.client:
            self._ensure_schema_exists()

    def _connect(self):
        try:
            print(f"Connecting to Weaviate at {self.weaviate_url}")
            # Connect to Weaviate using v4 client with better timeout settings
            additional_config = AdditionalConfig(
                # Increased timeouts
                timeout=Timeout(init=30, query=60, insert=120)
            )

            try:
                # Try with full connection first
                self.client = weaviate.connect_to_weaviate_cloud(
                    cluster_url=self.weaviate_url,
                    auth_credentials=Auth.api_key(self.weaviate_api_key),
                    additional_config=additional_config
                )

                # Test connection
                is_ready = self.client.is_ready()
                print("Client is ready:", is_ready)

                if is_ready:
                    self._ensure_schema_exists()
                    return

            except Exception as grpc_error:
                print(f"gRPC connection failed: {grpc_error}")
                print("Trying with skip_init_checks=True...")

                # Fallback: Skip init checks if gRPC fails
                self.client = weaviate.connect_to_weaviate_cloud(
                    cluster_url=self.weaviate_url,
                    auth_credentials=Auth.api_key(self.weaviate_api_key),
                    additional_config=additional_config,
                    skip_init_checks=True  # Skip gRPC health checks
                )

                print("Connected with skip_init_checks=True")
                self._ensure_schema_exists()
                return

        except Exception as e:
            print(f"Failed to connect to Weaviate: {str(e)}")
            self.client = None

    def __del__(self):
        """Cleanup when the instance is destroyed"""
        if hasattr(self, 'client') and self.client:
            self.client.close()

    def _ensure_schema_exists(self):
        """Ensure the Parts and Repairs collections exist"""
        try:
            print("Checking for existing collections...")

            # Check if Parts collection exists (real data)
            if not self.client.collections.exists("Parts"):
                print("Creating Parts collection...")
                self.client.collections.create(
                    name="Parts",
                    vectorizer_config=Configure.Vectorizer.text2vec_weaviate(),
                    properties=[
                        Property(name="applianceType",
                                 data_type=DataType.TEXT),
                        Property(name="partName", data_type=DataType.TEXT),
                        Property(name="partId", data_type=DataType.TEXT),
                        Property(name="brand", data_type=DataType.TEXT),
                        Property(name="price", data_type=DataType.NUMBER),
                        Property(name="availability", data_type=DataType.TEXT),
                        Property(name="productDescription",
                                 data_type=DataType.TEXT),
                        Property(name="productUrl", data_type=DataType.TEXT),
                        Property(name="youtubeVideoUrl",
                                 data_type=DataType.TEXT),
                        Property(name="compatibleModels",
                                 data_type=DataType.TEXT),
                        Property(name="sourcePage", data_type=DataType.TEXT)
                    ]
                )
                print("Parts collection created successfully")
            else:
                print("Parts collection already exists")

            # Check if Repairs collection exists (real data)
            if not self.client.collections.exists("Repairs"):
                print("Creating Repairs collection...")
                self.client.collections.create(
                    name="Repairs",
                    vectorizer_config=Configure.Vectorizer.text2vec_weaviate(),
                    properties=[
                        Property(name="product", data_type=DataType.TEXT),
                        Property(name="symptom", data_type=DataType.TEXT),
                        Property(name="description", data_type=DataType.TEXT),
                        Property(name="percentage", data_type=DataType.NUMBER),
                        Property(name="parts", data_type=DataType.TEXT_ARRAY),
                        Property(name="difficulty", data_type=DataType.TEXT),
                        Property(name="repairVideoUrl",
                                 data_type=DataType.TEXT)
                    ]
                )
                print("Repairs collection created successfully")
            else:
                print("Repairs collection already exists")

        except Exception as e:
            print(f"Error in schema setup: {str(e)}")

    def add_part(self, part_data: dict):
        """Add a part to the vector database"""
        if not self.client:
            return False

        try:
            # Transform CSV column names to camelCase for Weaviate
            transformed_data = {
                "applianceType": part_data.get("appliance_type"),
                "partName": part_data.get("part_name"),
                "partId": part_data.get("part_id"),
                "brand": part_data.get("brand"),
                "price": float(part_data.get("price", "0").replace("$", "").strip() or 0),
                "availability": part_data.get("availability"),
                "productDescription": part_data.get("product_description"),
                "productUrl": part_data.get("product_url"),
                "youtubeVideoUrl": part_data.get("youtube_video_url"),
                "compatibleModels": part_data.get("compatible_models"),
                "sourcePage": part_data.get("source_page")
            }

            # Create object using v4 API
            part_collection = self.client.collections.get("Parts")
            part_collection.data.insert(transformed_data)
            return True
        except Exception as e:
            print(f"Error adding part: {e}")
            return False

    def add_repair(self, repair_data: dict):
        """Add a repair to the vector database"""
        if not self.client:
            return False

        try:
            # Ensure parts is a list
            if isinstance(repair_data.get("parts"), str):
                repair_data["parts"] = [repair_data["parts"]]
            elif not isinstance(repair_data.get("parts"), list):
                repair_data["parts"] = []

            # Convert percentage to float if it exists
            if "percentage" in repair_data:
                try:
                    repair_data["percentage"] = float(
                        repair_data["percentage"])
                except (ValueError, TypeError):
                    repair_data["percentage"] = 0.0

            repair_collection = self.client.collections.get("Repairs")
            repair_collection.data.insert(repair_data)
            return True
        except Exception as e:
            print(f"Error adding repair: {e}")
            return False

    def add_blog(self, blog_data: dict):
        """Add a blog to the vector database"""
        if not self.client:
            return False

        try:
            blog_collection = self.client.collections.get("Blogs")
            blog_collection.data.insert(blog_data)
            return True
        except Exception as e:
            print(f"Error adding blog: {e}")
            return False

    def search_parts(self, query: str, limit: int = 5):
        """Search for parts using semantic search - optimized with caching"""
        if not self.client:
            return None

        # Check cache first using SimpleCache
        cache_key = self.cache._generate_key("search_parts", query, limit)
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result

        try:
            part_collection = self.client.collections.get("Parts")

            # First try exact match by partId (fastest query) - case insensitive
            if len(query) > 5 and query.upper().startswith(('PS', 'WP', 'W10')):  # Common part ID patterns
                # Convert query to uppercase for case-insensitive matching
                upper_query = query.upper()
                exact_matches = part_collection.query.fetch_objects(
                    filters=Filter.by_property("partId").equal(upper_query),
                    limit=1
                )
                if exact_matches.objects:
                    result = {
                        "data": {"Get": {"Part": [obj.properties for obj in exact_matches.objects]}}}
                    self.cache.set(cache_key, result)
                    return result

                # For part number queries, if no exact match, return empty result
                # This will trigger the fallback logic in partAgent
                result = {"data": {"Get": {"Part": []}}}
                self.cache.set(cache_key, result)
                return result

            # For non-part-number queries, do semantic search
            results = part_collection.query.near_text(
                query=query,
                limit=min(limit, 3)  # Cap at 3 results for faster response
            )
            result = {
                "data": {"Get": {"Part": [obj.properties for obj in results.objects]}}}
            self.cache.set(cache_key, result)
            return result
        except Exception as e:
            print(f"Error searching parts: {e}")
            return None

    def search_repairs(self, query: str, product: str = None, limit: int = 5):
        """Search repair data by symptom or description"""
        if not self.client:
            return None

        try:
            repair_collection = self.client.collections.get("Repairs")

            if product:
                results = repair_collection.query.near_text(
                    query=query,
                    filters=Filter.by_property("product").equal(product),
                    limit=limit
                )
            else:
                results = repair_collection.query.near_text(
                    query=query,
                    limit=limit
                )

            return {"data": {"Get": {"Repair": [obj.properties for obj in results.objects]}}}
        except Exception as e:
            print(f"Error searching repairs: {e}")
            return None

    def search_blogs(self, query: str, category: str = None, content_type: str = None, limit: int = 5):
        """Search blog data by title or content - optimized"""
        if not self.client:
            return None

        try:
            blog_collection = self.client.collections.get("Blogs")

            # Optimized: Start with smaller result set for faster processing
            response = blog_collection.query.near_text(
                query=query,
                limit=min(limit * 2, 20),  # Reduced from 100
                return_metadata=MetadataQuery(score=True)
            )

            results = []
            for obj in response.objects:
                # Fast filtering - break early when we have enough results
                if len(results) >= limit:
                    break

                # Apply filters if specified (simplified logic)
                if category and obj.properties.get("category") != category:
                    continue
                if content_type and obj.properties.get("content_type") != content_type:
                    continue

                results.append({
                    "title": obj.properties.get("title"),
                    "url": obj.properties.get("url"),
                    "category": obj.properties.get("category"),
                    "content_type": obj.properties.get("content_type"),
                    "score": obj.metadata.score if obj.metadata else None
                })

            return {"data": {"Get": {"Blog": results}}}
        except Exception as e:
            print(f"Error searching blogs: {e}")
            return None

    def get_part_by_id(self, part_id: str):
        """Get a specific part by its ID"""
        if not self.client:
            return None

        try:
            part_collection = self.client.collections.get("Parts")
            # Convert part_id to uppercase for case-insensitive matching
            upper_part_id = part_id.upper()
            results = part_collection.query.fetch_objects(
                filters=Filter.by_property("partId").equal(upper_part_id),
                limit=1
            )
            return {"data": {"Get": {"Part": [obj.properties for obj in results.objects]}}}
        except Exception as e:
            print(f"Error getting part: {e}")
            return None

    def find_compatible_parts(self, model_number: str):
        """Find parts compatible with a specific model number"""
        if not self.client:
            return None

        try:
            part_collection = self.client.collections.get("Parts")
            results = part_collection.query.fetch_objects(
                filters=Filter.by_property(
                    "compatibleModels").like(f"*{model_number}*")
            )
            return {"data": {"Get": {"Part": [obj.properties for obj in results.objects]}}}
        except Exception as e:
            print(f"Error finding compatible parts: {e}")
            return None

    def check_part_compatibility(self, part_id: str, model_number: str):
        """Check if a specific part is compatible with a specific model number"""
        if not self.client:
            return None

        try:
            part_collection = self.client.collections.get("Parts")

            # Get the specific part first - case insensitive
            upper_part_id = part_id.upper()
            part_results = part_collection.query.fetch_objects(
                filters=Filter.by_property("partId").equal(upper_part_id),
                limit=1
            )

            if not part_results.objects:
                return {
                    "compatible": False,
                    "reason": f"Part {part_id} not found in our database",
                    "part": None
                }

            part = part_results.objects[0].properties
            compatible_models = part.get("compatibleModels", "")

            # Check if Weaviate filtered the content
            if "[FILTERED:" in compatible_models or "unsafe content" in compatible_models.lower():
                return {
                    "compatible": "unknown",
                    "reason": f"I found part {part_id} ({part.get('partName', 'Unknown Part')}), but I can't check model compatibility right now due to a technical issue. Please contact our support team or check the manufacturer's website to verify if this part works with model {model_number}.",
                    "part": part,
                    "part_name": part.get('partName', 'Unknown Part'),
                    "part_description": part.get('productDescription', ''),
                    "support_needed": True
                }

            # Check if the model number is in the compatible models
            if model_number.upper() in compatible_models.upper():
                return {
                    "compatible": True,
                    "reason": f"Yes! Part {part_id} ({part.get('partName', 'Unknown Part')}) is compatible with model {model_number}",
                    "part": part
                }
            else:
                return {
                    "compatible": False,
                    "reason": f"No, part {part_id} ({part.get('partName', 'Unknown Part')}) is not compatible with model {model_number}",
                    "part": part,
                    "supported_models": compatible_models
                }

        except Exception as e:
            print(f"Error checking part compatibility: {e}")
            return None
