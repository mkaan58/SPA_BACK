# spa/services/fastmcp_photo_service.py
import json
import os
import asyncio
import logging
import time
import hashlib
from dataclasses import dataclass
from google.genai import types
from typing import Optional, List, Dict, Union
import httpx
from dotenv import load_dotenv
from django.conf import settings
from google import genai

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class UnsplashPhoto:
    id: str
    description: Optional[str]
    urls: Dict[str, str]
    width: int
    height: int
    quality_score: float = 0.0
    context_match: float = 0.0

class PhotoCache:
    """🚀 Simple caching"""
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 1800  # 30 dakika
    
    def get_cache_key(self, query: str) -> str:
        return hashlib.md5(query.encode()).hexdigest()
    
    def get_cached_photos(self, cache_key: str) -> Optional[List[UnsplashPhoto]]:
        if cache_key in self.cache:
            timestamp, photos = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return photos
        return None
    
    def cache_photos(self, cache_key: str, photos: List[UnsplashPhoto]):
        self.cache[cache_key] = (time.time(), photos)

class ContextAwarePhotoService:
    """
    🚀 SIMPLE & FAST Context-aware photo service
    No bullshit, just works!
    """
    
    def __init__(self):
        self.access_key = getattr(settings, 'UNSPLASH_ACCESS_KEY', None) or os.getenv("UNSPLASH_ACCESS_KEY")
        if not self.access_key:
            logger.error("❌ UNSPLASH_ACCESS_KEY not found!")
            raise ValueError("Missing UNSPLASH_ACCESS_KEY")
        
        self.photo_cache = PhotoCache()
        self.http_client = None
        
        logger.info("🚀 SIMPLE AI-Enhanced ContextAwarePhotoService initialized")
    
    async def get_http_client(self):
        """Reuse HTTP client"""
        if not self.http_client:
            self.http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(6.0),
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
            )
        return self.http_client
    
    async def close(self):
        if self.http_client:
            await self.http_client.aclose()

    # 🎯 MAIN SIMPLE METHOD

    async def get_context_aware_photos(
        self,
        design_plan: str,
        user_preferences: Dict,
        section_requirements: List[Dict] = None
    ) -> Dict[str, str]:
        """
        🚀 SIMPLE & FAST photo generation
        Target: 30-45 seconds, high success rate
        """
        start_time = time.time()
        logger.info("🚀 Starting SIMPLE Fast photo generation...")
        
        try:
            # 🎯 PHASE 1: SIMPLE PARSING
            requirements = await self._simple_parse_requirements(design_plan)
            business_type = requirements["business_type"]
            sections = requirements["sections"]
            
            logger.info(f"📊 Business: {business_type}, {requirements['total_images_needed']} images needed")
            
            # 🎯 PHASE 2: SIMPLE QUERY GENERATION
            all_queries = self._generate_simple_queries(sections, business_type)
            
            # 🎯 PHASE 3: PARALLEL SIMPLE SEARCH
            photo_tasks = []
            task_metadata = []
            
            for section_name, section_data in sections.items():
                section_queries = all_queries.get(section_name, [f"{business_type} {section_name}"])
                
                if section_data["count"] > 1:
                    for i in range(section_data["count"]):
                        query = section_queries[i % len(section_queries)]
                        task = asyncio.create_task(self._get_photo_simple(query, section_name))
                        photo_tasks.append(task)
                        task_metadata.append(f'{section_name}_{i+1}')
                else:
                    query = section_queries[0]
                    orientation = "landscape" if section_name == "hero" else None
                    task = asyncio.create_task(self._get_photo_simple(query, section_name, orientation))
                    photo_tasks.append(task)
                    task_metadata.append(f'{section_name}_image')
            
            logger.info(f"🔍 Executing {len(photo_tasks)} parallel searches...")
            
            # Execute in batches
            batch_size = 5
            all_results = []
            
            for i in range(0, len(photo_tasks), batch_size):
                batch = photo_tasks[i:i+batch_size]
                batch_results = await asyncio.gather(*batch, return_exceptions=True)
                all_results.extend(batch_results)
                
                if i + batch_size < len(photo_tasks):
                    await asyncio.sleep(0.2)  # Small delay
            
            # 🎯 PHASE 4: COMPILE RESULTS
            section_photos = {}
            success_count = 0
            
            for key, result in zip(task_metadata, all_results):
                if isinstance(result, Exception):
                    logger.error(f"❌ {key} failed: {result}")
                    section_photos[key] = self._get_emergency_url(business_type, key)
                elif result:
                    section_photos[key] = result
                    success_count += 1
                else:
                    section_photos[key] = self._get_emergency_url(business_type, key)
            
            total_time = time.time() - start_time
            logger.info(f"🎉 SIMPLE COMPLETED: {success_count}/{len(photo_tasks)} photos in {total_time:.1f} seconds")
            
            return section_photos
            
        except Exception as e:
            logger.error(f"❌ Simple generation failed: {e}")
            return self._get_emergency_fallback()

    async def _get_photo_simple(
        self, 
        query: str, 
        section_name: str, 
        orientation: Optional[str] = None
    ) -> Optional[str]:
        """
        🔍 Simple photo search with basic quality check
        """
        try:
            # Search photos
            photos = await self.search_photos_simple(
                query=query,
                per_page=8,
                orientation=orientation
            )
            
            if not photos:
                logger.warning(f"⚠️ No photos for: {query}")
                return None
            
            # Simple quality check - just use the best scoring one
            best_photo = max(photos, key=lambda p: p.quality_score + p.context_match)
            
            # Basic relevance check
            if self._simple_relevance_check(best_photo, query):
                url = best_photo.urls['regular']
                
                # Optimize hero images
                if section_name == "hero":
                    url = f"{url}&w=1200&h=600&fit=crop&crop=center"
                
                logger.info(f"✅ {section_name}: {query}")
                return url
            
            # If first photo not relevant, try second best
            if len(photos) > 1:
                second_best = photos[1]
                if self._simple_relevance_check(second_best, query):
                    return second_best.urls['regular']
            
            # Just use the best quality photo anyway
            logger.info(f"🔄 Using best quality for: {query}")
            return best_photo.urls['regular']
            
        except Exception as e:
            logger.error(f"❌ Photo search failed: {e}")
            return None

    def _simple_relevance_check(self, photo: UnsplashPhoto, query: str) -> bool:
        """
        ⚡ Super simple relevance check - no AI needed
        """
        if not photo.description:
            return True  # If no description, just accept it
        
        description = photo.description.lower()
        query_words = query.lower().split()
        
        # Check if any query word is in description
        return any(word in description for word in query_words if len(word) > 3)

    async def search_photos_simple(
        self,
        query: str,
        per_page: int = 10,
        orientation: Optional[str] = None
    ) -> List[UnsplashPhoto]:
        """
        🚀 Simple photo search with caching
        """
        # Check cache
        cache_key = self.photo_cache.get_cache_key(f"{query}_{per_page}_{orientation}")
        cached = self.photo_cache.get_cached_photos(cache_key)
        if cached:
            return cached[:per_page]
        
        # Random page for variety
        import random
        page = random.randint(1, 3)
        
        params = {
            "query": query,
            "page": page,
            "per_page": min(per_page, 30),
            "order_by": "relevant",
        }
        
        if orientation:
            params["orientation"] = orientation
        
        headers = {
            "Accept-Version": "v1",
            "Authorization": f"Client-ID {self.access_key}"
        }
        
        try:
            client = await self.get_http_client()
            response = await client.get(
                "https://api.unsplash.com/search/photos",
                params=params,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            
            photos = []
            for photo in data["results"]:
                unsplash_photo = UnsplashPhoto(
                    id=photo["id"],
                    description=photo.get("description"),
                    urls=photo["urls"],
                    width=photo["width"],
                    height=photo["height"]
                )
                
                # Simple scoring
                unsplash_photo.quality_score = self._calculate_quality_score(photo)
                unsplash_photo.context_match = self._calculate_context_match(photo, query)
                
                photos.append(unsplash_photo)
            
            # Sort by score
            photos.sort(key=lambda p: p.quality_score + p.context_match, reverse=True)
            
            # Cache results
            self.photo_cache.cache_photos(cache_key, photos)
            
            return photos
                
        except Exception as e:
            logger.error(f"❌ Search error: {e}")
            return []

    async def _simple_parse_requirements(self, design_plan: str) -> Dict:
        """
        🎯 Simple requirement parsing - no over-engineering
        """
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            simple_prompt = f"""
Parse this design plan and extract:
1. Business type (1-2 words max)
2. Sections that need images and how many

DESIGN PLAN:
{design_plan}

Return this JSON:
{{
  "business_type": "simple_business_type",
  "total_images_needed": number,
  "sections": {{
    "section_name": {{"count": number, "keywords": "simple keywords"}}
  }}
}}

Examples:
- "tailored suits company" → "suits"
- "premium meat seller" → "butcher" 
- "fitness gym" → "fitness"

Keep it SIMPLE. Don't use "/" or long phrases.
"""

            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=simple_prompt)],
                ),
            ]
            
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                contents=contents,
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            
            requirements = json.loads(response.text.strip())
            
            # Clean up business type
            business_type = requirements["business_type"].lower()
            if "/" in business_type:
                business_type = business_type.split("/")[0]
            if len(business_type.split()) > 2:
                business_type = business_type.split()[0]
            
            requirements["business_type"] = business_type
            
            return requirements
            
        except Exception as e:
            logger.error(f"❌ Parsing failed: {e}")
            return self._fallback_requirements(design_plan)

    def _fallback_requirements(self, design_plan: str) -> Dict:
        """Simple fallback parsing"""
        import re
        
        plan_lower = design_plan.lower()
        
        # Simple business type detection
        if 'suit' in plan_lower or 'tailor' in plan_lower:
            business_type = 'suits'
        elif 'butcher' in plan_lower or 'meat' in plan_lower:
            business_type = 'butcher'
        elif 'restaurant' in plan_lower or 'food' in plan_lower:
            business_type = 'restaurant'
        elif 'fitness' in plan_lower or 'gym' in plan_lower:
            business_type = 'fitness'
        elif 'tech' in plan_lower or 'software' in plan_lower:
            business_type = 'tech'
        else:
            business_type = 'business'
        
        # Count detection
        count_match = re.search(r'(\d+)\s+(photo|image)', plan_lower)
        gallery_count = int(count_match.group(1)) if count_match else 4
        
        return {
            "business_type": business_type,
            "total_images_needed": gallery_count + 2,
            "sections": {
                "hero": {"count": 1, "keywords": f"{business_type} professional"},
                "about": {"count": 1, "keywords": f"{business_type} team"},
                "gallery": {"count": gallery_count, "keywords": f"{business_type} work"}
            }
        }

    def _generate_simple_queries(self, sections: Dict, business_type: str) -> Dict[str, List[str]]:
        """
        🎯 SIMPLE query generation - no AI complexity
        """
        
        # Simple templates per business type
        business_templates = {
            'butcher': [
                'fresh meat cuts', 'butcher shop', 'raw beef steak', 'meat counter', 
                'premium beef', 'meat selection', 'fresh steaks', 'butcher work'
            ],
            'suits': [
                'men suit formal', 'business suit', 'elegant suit', 'formal wear',
                'tailored suit', 'suit fitting', 'businessman suit', 'formal attire'
            ],
            'restaurant': [
                'restaurant food', 'gourmet meal', 'chef cooking', 'dining experience',
                'food plating', 'restaurant interior', 'culinary art', 'fine dining'
            ],
            'fitness': [
                'gym workout', 'fitness training', 'exercise equipment', 'gym interior',
                'fitness activity', 'workout session', 'gym facility', 'sports training'
            ],
            'tech': [
                'office workspace', 'computer work', 'tech startup', 'modern office',
                'software development', 'tech team', 'digital work', 'coding workspace'
            ],
            'business': [
                'professional office', 'business meeting', 'corporate environment', 'workplace',
                'business team', 'office interior', 'professional service', 'business workspace'
            ]
        }
        
        templates = business_templates.get(business_type, business_templates['business'])
        
        all_queries = {}
        
        for section_name, section_data in sections.items():
            count = section_data["count"]
            queries = []
            
            for i in range(count):
                template = templates[i % len(templates)]
                
                # Section-specific modifications
                if section_name == "hero":
                    query = f"{template} professional background"
                elif section_name == "about":
                    query = f"{business_type} professional portrait"
                else:
                    query = template
                
                queries.append(query)
            
            all_queries[section_name] = queries
        
        logger.info(f"🎯 Simple queries for {business_type}:")
        for section, queries in all_queries.items():
            logger.info(f"   {section}: {queries}")
        
        return all_queries

    def _get_emergency_url(self, business_type: str, key: str) -> str:
        """Business-specific emergency URLs"""
        
        emergency_map = {
            'butcher': {
                'hero': 'https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=1200&h=600&fit=crop',
                'about': 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400&h=400&fit=crop',
                'default': 'https://images.unsplash.com/photo-1588347818123-7e6f4c57f7b7?w=600&h=400&fit=crop'
            },
            'suits': {
                'hero': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=1200&h=600&fit=crop',
                'about': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop',
                'default': 'https://images.unsplash.com/photo-1594736797933-d0d9eb1f0eb5?w=600&h=400&fit=crop'
            },
            'default': {
                'hero': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200&h=600&fit=crop',
                'about': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop',
                'default': 'https://images.unsplash.com/photo-1467232004584-a241de8bcf5d?w=600&h=400&fit=crop'
            }
        }
        
        business_map = emergency_map.get(business_type, emergency_map['default'])
        
        if 'hero' in key:
            return business_map['hero']
        elif 'about' in key:
            return business_map['about']
        else:
            return business_map['default']

    def _get_emergency_fallback(self) -> Dict[str, str]:
        """Emergency fallback"""
        return {
            'hero_image': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200&h=600&fit=crop',
            'about_image': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop',
            'gallery_1': 'https://images.unsplash.com/photo-1467232004584-a241de8bcf5d?w=600&h=400&fit=crop',
            'gallery_2': 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=600&h=400&fit=crop',
            'gallery_3': 'https://images.unsplash.com/photo-1553877522-43269d4ea984?w=600&h=400&fit=crop',
            'gallery_4': 'https://images.unsplash.com/photo-1551434678-e076c223a692?w=600&h=400&fit=crop'
        }

    # 🔄 PRESERVED METHODS FOR COMPATIBILITY

    def _calculate_quality_score(self, photo: Dict) -> float:
        """Simple quality scoring"""
        score = 0.0
        
        width = photo.get("width", 0)
        height = photo.get("height", 0)
        if width > 2000 and height > 1000:
            score += 0.3
        elif width > 1000 and height > 600:
            score += 0.2
        
        if photo.get("description"):
            score += 0.2
        
        likes = photo.get("likes", 0)
        if likes > 100:
            score += 0.3
        elif likes > 50:
            score += 0.2
        elif likes > 10:
            score += 0.1
        
        user = photo.get("user", {})
        if user.get("total_photos", 0) > 100:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_context_match(self, photo: Dict, query: str) -> float:
        """Simple context matching"""
        score = 0.0
        query_words = query.lower().split()
        
        description = photo.get("description", "") or ""
        alt_description = photo.get("alt_description", "") or ""
        text_to_check = f"{description} {alt_description}".lower()
        
        matches = sum(1 for word in query_words if len(word) > 3 and word in text_to_check)
        if matches > 0:
            score += (matches / len([w for w in query_words if len(w) > 3])) * 0.5
        
        tags = photo.get("tags", [])
        if tags:
            tag_names = [tag.get("title", "").lower() for tag in tags]
            tag_matches = sum(1 for word in query_words if len(word) > 3 and any(word in tag for tag in tag_names))
            if tag_matches > 0:
                score += (tag_matches / len([w for w in query_words if len(w) > 3])) * 0.3
        
        return min(score, 1.0)

    # Legacy compatibility methods
    async def get_context_aware_photos_with_verification(self, design_plan, user_preferences, section_requirements=None):
        return await self.get_context_aware_photos(design_plan, user_preferences, section_requirements)

    async def search_photos(self, query: str, page: Union[int, str] = 1, per_page: Union[int, str] = 10, 
                          order_by: str = "relevant", color: Optional[str] = None, 
                          orientation: Optional[str] = None, randomize: bool = True) -> List[UnsplashPhoto]:
        return await self.search_photos_simple(query, per_page, orientation)


# Singleton instance
context_aware_photo_service = ContextAwarePhotoService()