# spa/services/fastmcp_photo_service.py
import json
import os
import asyncio
import logging
from dataclasses import dataclass
from google.genai import types  # 🔥 DOĞRU IMPORT
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

class ContextAwarePhotoService:
    """
    AI-Enhanced FastMCP tabanlı context-aware fotoğraf servisi
    İçerik bazlı akıllı resim seçimi + AI-powered diversification
    """
    
    def __init__(self):
        self.access_key = getattr(settings, 'UNSPLASH_ACCESS_KEY', None) or os.getenv("UNSPLASH_ACCESS_KEY")
        if not self.access_key:
            logger.error("❌ UNSPLASH_ACCESS_KEY not found!")
            raise ValueError("Missing UNSPLASH_ACCESS_KEY")
        
        logger.info("✅ AI-Enhanced ContextAwarePhotoService initialized")
    
    async def search_photos(
        self,
        query: str,
        page: Union[int, str] = 1,
        per_page: Union[int, str] = 10,
        order_by: str = "relevant",
        color: Optional[str] = None,
        orientation: Optional[str] = None,
        randomize: bool = True
    ) -> List[UnsplashPhoto]:
        """
        Enhanced search with AI-powered randomization
        """
        
        # Type conversion
        try:
            page_int = int(page)
        except (ValueError, TypeError):
            page_int = 1
        
        try:
            per_page_int = int(per_page)
        except (ValueError, TypeError):
            per_page_int = 10
        
        # 🎲 AI-powered random page offset for diversity
        if randomize and page_int == 1:
            import random
            page_offset = random.randint(1, 3)
            page_int = page_offset
            logger.info(f"🎲 Using AI random page offset: {page_int}")
        
        params = {
            "query": query,
            "page": page_int,
            "per_page": min(per_page_int, 30),
            "order_by": order_by,
        }
        
        if color:
            params["color"] = color
        if orientation:
            params["orientation"] = orientation
        
        headers = {
            "Accept-Version": "v1",
            "Authorization": f"Client-ID {self.access_key}"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.unsplash.com/search/photos",
                    params=params,
                    headers=headers,
                    timeout=10
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
                    
                    # Context scoring ekle
                    unsplash_photo.quality_score = self._calculate_quality_score(photo)
                    unsplash_photo.context_match = self._calculate_context_match(photo, query)
                    
                    photos.append(unsplash_photo)
                
                # Score'a göre sırala
                photos.sort(key=lambda p: p.quality_score + p.context_match, reverse=True)
                
                logger.info(f"✅ Found {len(photos)} photos for query: {query}")
                return photos
                
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ Request error: {str(e)}")
            raise
    
    def _calculate_quality_score(self, photo: Dict) -> float:
        """Fotoğraf kalite skoru hesapla"""
        score = 0.0
        
        # Boyut skoru (büyük resimler daha kaliteli)
        width = photo.get("width", 0)
        height = photo.get("height", 0)
        if width > 2000 and height > 1000:
            score += 0.3
        elif width > 1000 and height > 600:
            score += 0.2
        
        # Açıklama var mı
        if photo.get("description"):
            score += 0.2
        
        # Beğeni sayısı (eğer varsa)
        likes = photo.get("likes", 0)
        if likes > 100:
            score += 0.3
        elif likes > 50:
            score += 0.2
        elif likes > 10:
            score += 0.1
        
        # User stats
        user = photo.get("user", {})
        if user.get("total_photos", 0) > 100:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_context_match(self, photo: Dict, query: str) -> float:
        """Context match skoru hesapla"""
        score = 0.0
        query_words = query.lower().split()
        
        # Açıklama kontrolü
        description = photo.get("description", "") or ""
        alt_description = photo.get("alt_description", "") or ""
        
        text_to_check = f"{description} {alt_description}".lower()
        
        # Kelime eşleşmesi
        matches = sum(1 for word in query_words if word in text_to_check)
        if matches > 0:
            score += (matches / len(query_words)) * 0.5
        
        # Tags kontrolü (eğer varsa)
        tags = photo.get("tags", [])
        if tags:
            tag_names = [tag.get("title", "").lower() for tag in tags]
            tag_matches = sum(1 for word in query_words if any(word in tag for tag in tag_names))
            if tag_matches > 0:
                score += (tag_matches / len(query_words)) * 0.3
        
        return min(score, 1.0)
    

    # Eski method yerine yeni verified version kullan:
    async def get_context_aware_photos(self, design_plan, user_preferences, section_requirements=None):
        return await self.get_context_aware_photos_with_verification(design_plan, user_preferences, section_requirements)
    
    # AI-POWERED QUALITY FILTERING & CONTEXT VERIFICATION

    async def search_photos_with_ai_verification(
        self,
        query: str,
        business_type: str,
        section_name: str,
        page: Union[int, str] = 1,
        per_page: Union[int, str] = 10,
        order_by: str = "relevant",
        color: Optional[str] = None,
        orientation: Optional[str] = None,
        max_attempts: int = 3
    ) -> List[UnsplashPhoto]:
        """
        🤖 AI-verified photo search - Alakasız resimleri filtreler
        """
        
        for attempt in range(max_attempts):
            try:
                # Normal search yap
                photos = await self.search_photos(
                    query=query,
                    page=page,
                    per_page=min(per_page * 2, 20),  # Daha fazla seçenek
                    order_by=order_by,
                    color=color,
                    orientation=orientation,
                    randomize=True
                )
                
                if not photos:
                    continue
                
                # 🤖 AI ile resimleri context verification
                verified_photos = await self._ai_verify_photo_relevance(
                    photos=photos,
                    query=query,
                    business_type=business_type,
                    section_name=section_name,
                    required_count=per_page
                )
                
                if verified_photos:
                    logger.info(f"✅ AI verified {len(verified_photos)}/{len(photos)} photos for: {query}")
                    return verified_photos
                else:
                    logger.warning(f"⚠️ No verified photos for attempt {attempt + 1}: {query}")
                    # Query'yi AI ile refine et
                    if attempt < max_attempts - 1:
                        query = await self._ai_refine_query_for_relevance(query, business_type, section_name, attempt + 1)
                        logger.info(f"🔧 Refining query attempt {attempt + 2}: {query}")
            
            except Exception as e:
                logger.error(f"❌ Search attempt {attempt + 1} failed: {e}")
        
        # Son çare: basit search
        logger.warning(f"🔄 Falling back to basic search for: {query}")
        return await self.search_photos(query=f"{business_type} {section_name}", per_page=per_page)

    async def _ai_verify_photo_relevance(
        self,
        photos: List[UnsplashPhoto],
        query: str, 
        business_type: str,
        section_name: str,
        required_count: int = 5
    ) -> List[UnsplashPhoto]:
        """
        🤖 AI ile fotoğrafların alakalılığını doğrula
        """
        
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            # Photo metadata'ları topla
            photo_descriptions = []
            for i, photo in enumerate(photos[:10]):  # İlk 10'u kontrol et
                description = photo.description or "No description"
                alt_description = getattr(photo, 'alt_description', '') or ""
                photo_descriptions.append({
                    "index": i,
                    "id": photo.id,
                    "description": description,
                    "alt_description": alt_description,
                    "width": photo.width,
                    "height": photo.height
                })
            
            verification_prompt = f"""
    You are an expert photo curator for business websites. Your job is to verify if photos are RELEVANT and HIGH-QUALITY for a specific business context.

    CONTEXT:
    - Business Type: {business_type}
    - Section: {section_name}
    - Search Query: {query}
    - Required Count: {required_count}

    PHOTOS TO EVALUATE:
    {json.dumps(photo_descriptions, indent=2)}

    EVALUATION CRITERIA:
    1. RELEVANCE: Does the photo clearly relate to {business_type} and {section_name}?
    2. QUALITY: Is it professional, well-lit, and high-resolution?
    3. CONTEXT FIT: Would this photo make sense on a {business_type} website's {section_name} section?

    STRICT FILTERING RULES:
    - For BAKERY GALLERY: Must show baked goods, bakery interior, or baking process
    - For RESTAURANT FOOD: Must show actual food, not random objects
    - For TECH PORTFOLIO: Must show technology, coding, or digital work
    - For FITNESS GYM: Must show exercise, equipment, or fitness activities

    REJECT photos that are:
    - Completely unrelated to the business type
    - Poor quality or blurry
    - Stock photos that look generic/fake
    - Wrong context (e.g., random nature photos for tech company)

    Return ONLY a JSON array of indices of APPROVED photos, ordered by relevance:
    [0, 2, 5, 1, 3]

    Choose the BEST {required_count} photos. If fewer than {required_count} are relevant, return only the good ones.
    """

            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=verification_prompt)],
                ),
            ]
            
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                contents=contents,
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            
            approved_indices = json.loads(response.text.strip())
            
            # Approved fotoğrafları döndür
            verified_photos = []
            for idx in approved_indices:
                if 0 <= idx < len(photos):
                    verified_photos.append(photos[idx])
                    logger.info(f"✅ AI approved photo {idx}: {photos[idx].description[:50] if photos[idx].description else 'No desc'}...")
            
            return verified_photos[:required_count]
            
        except Exception as e:
            logger.error(f"❌ AI verification failed: {e}")
            # Fallback: return first few photos
            return photos[:required_count]

    async def _ai_refine_query_for_relevance(
        self,
        original_query: str,
        business_type: str, 
        section_name: str,
        attempt: int
    ) -> str:
        """
        🔧 Alakasız sonuçlar için query'yi AI ile refine et
        """
        
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            refine_prompt = f"""
    The search query "{original_query}" for {business_type} {section_name} is returning irrelevant photos.

    PROBLEM: Photos are not matching the business context properly.

    TASK: Create a MORE SPECIFIC query that will return highly relevant {business_type} photos for {section_name}.

    REFINEMENT STRATEGIES:
    1. Add more specific {business_type} terms
    2. Include action words or specific objects
    3. Add quality/style descriptors
    4. Focus on the exact business context

    EXAMPLES:
    Original: "elegant celebration cake floral decoration"
    Refined: "bakery wedding cake display fresh flowers commercial quality"

    Original: "modern office workspace"  
    Refined: "professional business office interior modern furniture"

    Create 1 refined query (4-8 words) that will get better {business_type} results:
    """

            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=refine_prompt)],
                ),
            ]
            
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                contents=contents,
                config=types.GenerateContentConfig(response_mime_type="text/plain"),
            )
            
            refined_query = response.text.strip()
            logger.info(f"🔧 AI refined: '{original_query}' → '{refined_query}'")
            return refined_query
            
        except:
            # Manual refinement fallback
            refinements = [
                f"{business_type} professional high quality",
                f"{business_type} commercial {section_name} display",
                f"{business_type} interior professional workspace"
            ]
            return f"{original_query} {refinements[attempt % len(refinements)]}"

    # 🎯 ENHANCED GET_CONTEXT_AWARE_PHOTOS WITH AI VERIFICATION

    async def get_context_aware_photos_with_verification(
        self,
        design_plan: str,
        user_preferences: Dict,
        section_requirements: List[Dict] = None
    ) -> Dict[str, str]:
        """
        🤖 AI-Enhanced + Verified Context-aware fotoğrafları getir
        """
        logger.info("🚀 Starting AI-Enhanced + Verified photo generation...")
        
        # Existing parsing logic...
        try:
            requirements = await self._parse_design_plan_requirements_async(design_plan)
            business_type = requirements["business_type"]
            sections = requirements["sections"]
            
            logger.info(f"📊 DYNAMIC PARSING RESULT:")
            logger.info(f"   Business Type: {business_type}")
            logger.info(f"   Total Images: {requirements['total_images_needed']}")
            logger.info(f"   Sections: {list(sections.keys())}")
            
        except Exception as e:
            logger.error(f"❌ Dynamic parsing failed: {e}")
            business_type = self._extract_business_type(design_plan, user_preferences)
            sections = self._get_default_sections(business_type)
            logger.warning(f"🔄 Using fallback: {business_type}")
        
        theme = user_preferences.get('theme', 'light')
        
        # 🤖 AI-VERIFIED SECTION-BASED PHOTO GENERATION
        section_photos = {}
        
        for section_name, section_data in sections.items():
            count = section_data["count"]
            keywords = section_data["keywords"]
            
            if count > 1:
                # 🔥 AI-VERIFIED MULTIPLE IMAGES GENERATION
                try:
                    logger.info(f"🤖 Generating AI-verified queries for {section_name} ({count} images)")
                    
                    # AI ile çeşitli query'ler oluştur
                    diverse_queries = await self._ai_generate_diverse_queries(
                        section_name=section_name,
                        base_keywords=keywords,
                        business_type=business_type,
                        count=count,
                        design_plan_context=design_plan[:500]
                    )
                    
                    logger.info(f"🎯 AI generated {len(diverse_queries)} diverse queries for {section_name}")
                    
                    for i in range(1, count + 1):
                        try:
                            query = diverse_queries[i-1] if i-1 < len(diverse_queries) else diverse_queries[-1]
                            
                            # 🤖 AI-VERIFIED SEARCH
                            verified_photos = await self.search_photos_with_ai_verification(
                                query=query,
                                business_type=business_type,
                                section_name=section_name,
                                per_page=3,
                                max_attempts=2
                            )
                            
                            if verified_photos:
                                # İlk verified fotoğrafı kullan
                                section_photos[f'{section_name}_{i}'] = verified_photos[0].urls['regular']
                                logger.info(f"✅ VERIFIED {section_name} {i}: {query[:50]}...")
                            else:
                                logger.warning(f"⚠️ No verified photos for {section_name} {i}")
                            
                        except Exception as e:
                            logger.error(f"❌ Error in verified generation {section_name}_{i}: {e}")
                            
                except Exception as ai_error:
                    logger.error(f"❌ AI verification failed for {section_name}: {ai_error}")
                    # Fallback to old system
                    section_photos.update(await self._manual_fallback_generation(section_name, keywords, business_type, count))
            
            else:
                # Single image sections with verification
                try:
                    orientation = "landscape" if section_name == "hero" else "portrait" if section_name == "about" else None
                    
                    # 🤖 AI-VERIFIED SINGLE IMAGE
                    verified_photos = await self.search_photos_with_ai_verification(
                        query=keywords,
                        business_type=business_type,
                        section_name=section_name,
                        per_page=1,
                        orientation=orientation,
                        max_attempts=2
                    )
                    
                    if verified_photos:
                        if section_name == "hero":
                            raw_url = verified_photos[0].urls['regular']
                            optimized_url = f"{raw_url}&w=1200&h=600&fit=crop&crop=center"
                            section_photos[f'{section_name}_image'] = optimized_url
                        else:
                            section_photos[f'{section_name}_image'] = verified_photos[0].urls['regular']
                        
                        logger.info(f"✅ VERIFIED {section_name}: {keywords}")
                    
                except Exception as e:
                    logger.error(f"❌ Error in verified single generation {section_name}: {e}")
        
        logger.info(f"🎉 Generated {len(section_photos)} AI-verified photos")
        return section_photos if section_photos else self._get_emergency_fallback()

    # 🎯 BONUS: SMART RETRY WITH DIFFERENT QUERY STRATEGIES

    async def _get_alternative_query_strategies(self, original_query: str, business_type: str, section_name: str) -> List[str]:
        """
        📝 Farklı query stratejileri oluştur
        """
        
        strategies = [
            f"{business_type} {section_name} professional commercial",  # Professional focus
            f"{business_type} {section_name} interior environment",      # Environmental focus  
            f"{business_type} {section_name} product service quality",   # Product/service focus
            f"{business_type} workplace professional modern",           # Workplace focus
            f"{original_query} high quality commercial"                 # Enhanced original
        ]
        
        return strategies[:3]  # En iyi 3'ü döndür
    # async def get_context_aware_photos(
    #     self,
    #     design_plan: str,
    #     user_preferences: Dict,
    #     section_requirements: List[Dict] = None
    # ) -> Dict[str, str]:
    #     """
    #     🤖 AI-Enhanced Context-aware fotoğrafları getir
    #     """
    #     logger.info("🚀 Starting AI-Enhanced context-aware photo generation...")
        
    #     # 🎯 DYNAMIC REQUIREMENTS PARSING (Existing)
    #     try:
    #         requirements = await self._parse_design_plan_requirements_async(design_plan)
    #         business_type = requirements["business_type"]
    #         sections = requirements["sections"]
            
    #         logger.info(f"📊 DYNAMIC PARSING RESULT:")
    #         logger.info(f"   Business Type: {business_type}")
    #         logger.info(f"   Total Images: {requirements['total_images_needed']}")
    #         logger.info(f"   Sections: {list(sections.keys())}")
            
    #     except Exception as e:
    #         logger.error(f"❌ Dynamic parsing failed: {e}")
    #         # Fallback to old method
    #         business_type = self._extract_business_type(design_plan, user_preferences)
    #         sections = self._get_default_sections(business_type)
    #         logger.warning(f"🔄 Using fallback: {business_type}")
        
    #     theme = user_preferences.get('theme', 'light')
        
    #     # 🤖 AI-POWERED DYNAMIC SECTION-BASED PHOTO GENERATION
    #     section_photos = {}
        
    #     for section_name, section_data in sections.items():
    #         count = section_data["count"]
    #         keywords = section_data["keywords"]
            
    #         if count > 1:
    #             # 🔥 AI-POWERED MULTIPLE IMAGES GENERATION
    #             try:
    #                 logger.info(f"🤖 Generating AI-diverse queries for {section_name} ({count} images)")
                    
    #                 # AI ile çeşitli query'ler oluştur
    #                 diverse_queries = await self._ai_generate_diverse_queries(
    #                     section_name=section_name,
    #                     base_keywords=keywords,
    #                     business_type=business_type,
    #                     count=count,
    #                     design_plan_context=design_plan[:500]  # Context için plan excerpt
    #                 )
                    
    #                 logger.info(f"🎯 AI generated {len(diverse_queries)} diverse queries for {section_name}")
                    
    #                 for i in range(1, count + 1):
    #                     try:
    #                         query = diverse_queries[i-1] if i-1 < len(diverse_queries) else diverse_queries[-1]
                            
    #                         # 🎲 Random page ve order için variety
    #                         page_num = ((i-1) % 3) + 1  # 1,2,3 rotasyonu
    #                         order_options = ['relevant', 'latest', 'popular']
    #                         order_by = order_options[i % len(order_options)]
                            
    #                         photos = await self.search_photos(
    #                             query=query,
    #                             per_page=8,  # Daha fazla seçenek
    #                             page=page_num,
    #                             order_by=order_by,
    #                             orientation="landscape" if section_name in ["portfolio", "gallery"] else None,
    #                             randomize=True
    #                         )
                            
    #                         if photos:
    #                             # Her seferinde farklı foto index (0,1,2 rotasyonu)
    #                             photo_index = (i-1) % min(len(photos), 3)
    #                             section_photos[f'{section_name}_{i}'] = photos[photo_index].urls['regular']
    #                             logger.info(f"✅ {section_name} {i}: {query[:50]}... (page:{page_num}, idx:{photo_index})")
                            
    #                     except Exception as e:
    #                         logger.error(f"❌ Error generating {section_name}_{i}: {e}")
    #                         # AI Fallback
    #                         try:
    #                             fallback_query = await self._ai_generate_fallback_query(business_type, section_name, i)
    #                             photos = await self.search_photos(fallback_query, per_page=5, randomize=True)
    #                             if photos:
    #                                 section_photos[f'{section_name}_{i}'] = photos[0].urls['regular']
    #                                 logger.info(f"🔄 {section_name} {i}: AI fallback used")
    #                         except:
    #                             logger.error(f"❌ AI fallback also failed for {section_name}_{i}")
                                
    #             except Exception as ai_error:
    #                 logger.error(f"❌ AI diversification failed for {section_name}: {ai_error}")
    #                 # Manual fallback to old system
    #                 logger.info(f"🔄 Falling back to manual system for {section_name}")
    #                 section_photos.update(await self._manual_fallback_generation(section_name, keywords, business_type, count))
            
    #         else:
    #             # Single image sections (Existing logic preserved)
    #             try:
    #                 orientation = "landscape" if section_name == "hero" else "portrait" if section_name == "about" else None
                    
    #                 photos = await self.search_photos(
    #                     query=keywords,
    #                     per_page=5,
    #                     orientation=orientation,
    #                     randomize=True
    #                 )
                    
    #                 if photos:
    #                     if section_name == "hero":
    #                         # Hero için optimize edilmiş URL
    #                         raw_url = photos[0].urls['regular']
    #                         optimized_url = f"{raw_url}&w=1200&h=600&fit=crop&crop=center"
    #                         section_photos[f'{section_name}_image'] = optimized_url
    #                     else:
    #                         section_photos[f'{section_name}_image'] = photos[0].urls['regular']
                        
    #                     logger.info(f"✅ {section_name}: {keywords}")
                    
    #             except Exception as e:
    #                 logger.error(f"❌ Error generating {section_name}: {e}")
        
    #     logger.info(f"🎉 Generated {len(section_photos)} AI-enhanced diverse photos")
    #     logger.info(f"📋 Final sections: {list(section_photos.keys())}")
        
    #     if not section_photos:
    #         logger.error("❌ No photos generated, returning emergency fallback")
    #         return self._get_emergency_fallback()
    #     return section_photos

    async def _ai_generate_diverse_queries(
        self, 
        section_name: str, 
        base_keywords: str, 
        business_type: str, 
        count: int,
        design_plan_context: str = ""
    ) -> List[str]:
        """
        🤖 AI ile çeşitli ve spesifik query'ler oluştur
        """
        
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            ai_prompt = f"""
You are a professional photography search expert and visual content strategist. 

TASK: Generate {count} completely different and specific search queries for {section_name} section images.

CONTEXT:
- Business Type: {business_type}
- Section: {section_name}
- Base Keywords: {base_keywords}
- Design Plan Context: {design_plan_context}

CRITICAL REQUIREMENTS:
1. Each query must be COMPLETELY DIFFERENT from others
2. Each query must target DIFFERENT aspects/angles of the business
3. Each query must be SPECIFIC enough to return different photos
4. Use CONCRETE, VISUAL terms that photographers would use
5. Focus on DIFFERENT products, services, or moments for each query

EXAMPLES of what makes queries DIFFERENT:
- Query 1: "fresh croissants golden brown bakery display morning"
- Query 2: "baker hands kneading dough flour kitchen action" 
- Query 3: "wedding cake multi tier elegant decoration"
- Query 4: "bakery interior customers coffee pastry atmosphere"

QUERY CATEGORIES to consider:
- Products/Services (different items each time)
- Process/Action (behind-the-scenes, work in progress)
- Atmosphere/Environment (different locations, moods)
- People/Interaction (customers, staff, community)
- Details/Close-ups (textures, ingredients, tools)
- Results/Outcomes (finished products, satisfied customers)

BUSINESS-SPECIFIC GUIDANCE:
Think about what makes {business_type} unique and create queries that showcase:
- Different products/services they offer
- Different aspects of their work process
- Different customer experiences
- Different physical environments
- Different professional moments

Generate EXACTLY {count} queries, each on a new line, with NO numbering or extra text.
Each query should be 4-8 words, highly specific and visual.

QUERIES:
"""

            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=ai_prompt)],
                ),
            ]
            
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                contents=contents,
                config=types.GenerateContentConfig(response_mime_type="text/plain"),
            )
            
            # Parse response
            queries = []
            lines = response.text.strip().split('\n')
            
            for line in lines:
                clean_line = line.strip()
                # Remove numbering if present
                if clean_line and not clean_line.startswith('#'):
                    # Remove numbers and dots from start
                    import re
                    clean_line = re.sub(r'^\d+\.?\s*', '', clean_line)
                    if clean_line:
                        queries.append(clean_line)
            
            # Ensure we have enough queries
            while len(queries) < count:
                queries.append(f"{business_type} {section_name} variation {len(queries) + 1}")
            
            # Log generated queries
            logger.info(f"🤖 AI Generated Diverse Queries for {section_name}:")
            for i, query in enumerate(queries[:count], 1):
                logger.info(f"   {i}: {query}")
            
            return queries[:count]
            
        except Exception as e:
            logger.error(f"❌ AI query generation failed: {e}")
            return await self._generate_fallback_queries(section_name, base_keywords, business_type, count)

    async def _ai_generate_fallback_query(self, business_type: str, section_name: str, variation_num: int) -> str:
        """
        🤖 AI ile tek fallback query oluştur
        """
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            prompt = f"""
Generate 1 specific search query for a {business_type} {section_name} image.
Make it variation #{variation_num}, so it should be different from typical results.
Use 4-6 specific visual words.
Focus on a unique aspect of {business_type} business.

Query:
"""
            
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)],
                ),
            ]
            
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                contents=contents,
                config=types.GenerateContentConfig(response_mime_type="text/plain"),
            )
            
            return response.text.strip()
            
        except:
            return f"{business_type} {section_name} unique variation {variation_num}"

    async def _generate_fallback_queries(self, section_name: str, base_keywords: str, business_type: str, count: int) -> List[str]:
        """
        AI olmadığında manuel fallback
        """
        
        # Basic variation patterns
        variations = [
            "modern professional clean",
            "traditional authentic handcrafted", 
            "creative artistic innovative",
            "elegant sophisticated premium",
            "rustic natural organic",
            "bright colorful vibrant",
            "detailed close up texture",
            "atmospheric moody lighting"
        ]
        
        queries = []
        base_term = base_keywords.split()[0] if base_keywords else business_type
        
        for i in range(count):
            variation = variations[i % len(variations)]
            query = f"{base_term} {variation} {section_name}"
            queries.append(query)
        
        logger.info(f"🔄 Manual fallback queries generated for {section_name}")
        return queries

    async def _manual_fallback_generation(self, section_name: str, keywords: str, business_type: str, count: int) -> Dict[str, str]:
        """
        Manual fallback when AI fails completely (Existing logic enhanced)
        """
        
        photos = {}
        
        # Enhanced manual variations
        enhanced_variations = [
            "modern professional", "creative artistic", "elegant sophisticated", 
            "rustic authentic", "bright colorful", "detailed close up",
            "atmospheric moody", "premium quality", "innovative design",
            "traditional classic", "contemporary stylish", "natural organic"
        ]
        
        for i in range(1, count + 1):
            try:
                # Use enhanced variations
                variation = enhanced_variations[(i-1) % len(enhanced_variations)]
                query = f"{business_type} {keywords} {variation}"
                
                # Different page and order for each
                page_num = ((i-1) % 3) + 1
                order_options = ['relevant', 'latest', 'popular']
                order_by = order_options[i % len(order_options)]
                
                search_photos = await self.search_photos(
                    query=query,
                    page=page_num,
                    per_page=5,
                    order_by=order_by,
                    randomize=True
                )
                
                if search_photos:
                    photo_index = (i-1) % min(len(search_photos), 3)
                    photos[f'{section_name}_{i}'] = search_photos[photo_index].urls['regular']
                    logger.info(f"🔄 Manual fallback {section_name} {i}: {query}")
            
            except Exception as e:
                logger.error(f"❌ Manual fallback failed for {section_name}_{i}: {e}")
        
        return photos

    # 🔥 EXISTING METHODS PRESERVED (No changes to working code)
    
    def _get_emergency_fallback(self) -> Dict[str, str]:
        """Emergency fallback images"""
        return {
            'hero_image': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200&h=600&fit=crop',
            'about_image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop',
            'portfolio_1': 'https://images.unsplash.com/photo-1467232004584-a241de8bcf5d?w=600&h=400&fit=crop',
            'portfolio_2': 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=600&h=400&fit=crop',
            'portfolio_3': 'https://images.unsplash.com/photo-1553877522-43269d4ea984?w=600&h=400&fit=crop',
            'service_image': 'https://images.unsplash.com/photo-1551434678-e076c223a692?w=800&h=500&fit=crop'
        }

    async def _parse_design_plan_requirements_async(self, design_plan: str) -> Dict:
        """Async design plan parsing (EXISTING - PRESERVED)"""
        
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            parse_prompt = f"""
    Analyze this design plan and extract ALL sections that require images with their exact counts.

    DESIGN PLAN:
    {design_plan}

    Extract information and return ONLY this JSON:

    {{
    "total_images_needed": TOTAL_COUNT,
    "business_type": "DETECTED_BUSINESS_TYPE",
    "sections": {{
        "SECTION_NAME": {{
        "count": NUMBER_OF_IMAGES,
        "keywords": "relevant keywords for this section"
        }}
    }}
    }}

    RULES:
    1. Look for business type: architecture, restaurant, tech, consulting, etc.
    2. Find ALL sections: hero, about, portfolio, services, gallery, team, etc.
    3. Count images for each section (if "7 photos" mentioned, use 7)
    4. Generate business-specific keywords
    5. Default portfolio count: 6 if not specified

    Return ONLY the JSON.
    """

            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=parse_prompt)],
                ),
            ]
            
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                contents=contents,
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            
            requirements = json.loads(response.text.strip())
            logger.info(f"🤖 AI parsed requirements: {requirements['business_type']}, {requirements['total_images_needed']} images")
            
            return requirements
            
        except Exception as e:
            logger.error(f"❌ Async parsing failed: {e}")
            return self._get_fallback_requirements(design_plan)

    def _get_fallback_requirements(self, design_plan: str) -> Dict:
        """Fallback requirements (EXISTING - PRESERVED)"""
        import re
        
        # Business type detection
        business_type = "general"
        business_patterns = {
            'architecture': r'\b(architect|architectural|building)\b',
            'restaurant': r'\b(restaurant|cafe|food|dining)\b',
            'consulting': r'\b(consulting|advisory|business)\b',
            'tech': r'\b(technology|software|app|digital)\b',
        }
        
        for btype, pattern in business_patterns.items():
            if re.search(pattern, design_plan, re.IGNORECASE):
                business_type = btype
                break
        
        # Portfolio count detection
        portfolio_match = re.search(r'(\d+)\s+(photo|image|project)', design_plan.lower())
        portfolio_count = int(portfolio_match.group(1)) if portfolio_match else 6
        
        return {
            "total_images_needed": portfolio_count + 3,
            "business_type": business_type,
            "sections": {
                "hero": {"count": 1, "keywords": f"{business_type} modern professional workspace"},
                "about": {"count": 1, "keywords": f"{business_type} team professional portrait"},
                "portfolio": {"count": portfolio_count, "keywords": f"{business_type} project showcase work"},
                "services": {"count": 1, "keywords": f"{business_type} service quality"}
            }
        }

    def _get_default_sections(self, business_type: str) -> Dict:
        """Default sections for fallback (EXISTING - PRESERVED)"""
        return {
            "hero": {"count": 1, "keywords": f"{business_type} modern workspace"},
            "about": {"count": 1, "keywords": f"{business_type} professional portrait"},
            "portfolio": {"count": 3, "keywords": f"{business_type} project showcase"},
            "services": {"count": 1, "keywords": f"{business_type} service quality"}
        }

    def _extract_business_type(self, design_plan: str, user_preferences: Dict) -> str:
        """Business type'ını extract et (EXISTING - PRESERVED)"""
        
        # User preferences'ten al
        if user_preferences.get('business_type'):
            return user_preferences['business_type']
        
        # Design plan'dan çıkar
        plan_lower = design_plan.lower()
        
        business_keywords = {
            'restaurant': ['restaurant', 'cafe', 'food', 'dining', 'culinary', 'chef'],
            'fitness': ['fitness', 'gym', 'workout', 'health', 'training', 'sport'],
            'photography': ['photography', 'photo', 'camera', 'portrait', 'wedding'],
            'law': ['law', 'lawyer', 'legal', 'attorney', 'justice'],
            'medical': ['medical', 'doctor', 'healthcare', 'clinic', 'hospital'],
            'technology': ['technology', 'software', 'app', 'digital', 'tech'],
            'real-estate': ['real estate', 'property', 'home', 'house'],
            'consulting': ['consulting', 'advisory', 'business'],
            'creative': ['design', 'creative', 'art', 'marketing'],
            'education': ['education', 'school', 'learning', 'course']
        }
        
        for business_type, keywords in business_keywords.items():
            if any(keyword in plan_lower for keyword in keywords):
                return business_type
        
        return 'professional'
    
    # ALL OTHER EXISTING METHODS PRESERVED EXACTLY AS THEY WERE...
    # (Keeping the working code intact)
    
    def _generate_hero_query(self, business_type: str, user_preferences: Dict) -> str:
        """Hero section için query oluştur (EXISTING - PRESERVED)"""
        
        base_queries = {
            'restaurant': 'modern restaurant interior elegant dining',
            'fitness': 'modern gym fitness equipment professional',
            'photography': 'photography studio professional lighting',
            'law': 'law office professional modern interior',
            'medical': 'medical clinic modern healthcare facility',
            'technology': 'modern office technology workspace',
            'real-estate': 'luxury modern home exterior',
            'consulting': 'modern office professional workspace',
            'creative': 'creative studio modern workspace',
            'education': 'modern classroom educational environment',
            'professional': 'modern office professional workspace'
        }
        
        base_query = base_queries.get(business_type, base_queries['professional'])
        
        # Theme'e göre modifier ekle
        theme = user_preferences.get('theme', 'light')
        if theme == 'dark':
            base_query += ' dark elegant sophisticated'
        else:
            base_query += ' bright clean modern'
        
        return base_query
    
    def _generate_about_query(self, business_type: str) -> str:
        """About section için query oluştur (EXISTING - PRESERVED)"""
        
        queries = {
            'restaurant': 'professional chef portrait kitchen',
            'fitness': 'fitness trainer professional portrait',
            'photography': 'photographer with camera professional',
            'law': 'lawyer professional business portrait',
            'medical': 'doctor healthcare professional portrait',
            'technology': 'tech professional developer portrait',
            'real-estate': 'real estate agent professional',
            'consulting': 'business consultant professional',
            'creative': 'creative professional designer',
            'education': 'teacher educator professional',
            'professional': 'business professional portrait'
        }
        
        return queries.get(business_type, queries['professional'])
    
    def _generate_portfolio_queries(self, business_type: str) -> List[str]:
            """Portfolio section için 3 farklı query oluştur (EXISTING - PRESERVED)"""
            
            portfolio_sets = {
                'restaurant': [
                    'gourmet food plating elegant',
                    'restaurant atmosphere dining',
                    'culinary creation beautiful food'
                ],
                'fitness': [
                    'fitness transformation success',
                    'gym equipment modern facility',
                    'workout training session'
                ],
                'photography': [
                    'professional portrait photography',
                    'wedding photography beautiful',
                    'landscape photography stunning'
                ],
                'law': [
                    'legal consultation professional',
                    'courtroom justice legal',
                    'legal documents contract'
                ],
                'medical': [
                    'medical consultation patient care',
                    'healthcare technology modern',
                    'medical team collaboration'
                ],
                'technology': [
                    'software development coding',
                    'mobile app interface',
                    'technology innovation digital'
                ],
                'real-estate': [
                    'luxury home interior design',
                    'modern property exterior',
                    'real estate investment'
                ],
                'consulting': [
                    'business strategy meeting',
                    'data analysis professional',
                    'consulting presentation'
                ],
                'creative': [
                    'graphic design creative work',
                    'marketing campaign creative',
                    'brand design project'
                ],
                'education': [
                    'online learning platform',
                    'educational resources modern',
                    'student success achievement'
                ],
                'professional': [
                    'business project success',
                    'professional collaboration',
                    'innovation technology'
                ]
            }
            
            return portfolio_sets.get(business_type, portfolio_sets['professional'])
    
    def _generate_service_query(self, business_type: str) -> str:
        """Service section için query oluştur (EXISTING - PRESERVED)"""
        
        queries = {
            'restaurant': 'restaurant service quality dining',
            'fitness': 'fitness training service professional',
            'photography': 'photography service professional quality',
            'law': 'legal service professional consultation',
            'medical': 'healthcare service medical quality',
            'technology': 'technology service innovation',
            'real-estate': 'real estate service professional',
            'consulting': 'consulting service business strategy',
            'creative': 'creative service design quality',
            'education': 'education service learning quality',
            'professional': 'professional service quality business'
        }
        
        return queries.get(business_type, queries['professional'])

    def _parse_design_plan_requirements(self, design_plan: str) -> Dict:
        """Design plan'dan DYNAMIC section requirements'ı parse et (EXISTING - PRESERVED)"""
        
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            parse_prompt = f"""
    Analyze this design plan and extract ALL sections that require images, regardless of section names.

    DESIGN PLAN:
    {design_plan}

    INSTRUCTIONS:
    1. Find ALL sections that mention images, photos, visuals, or backgrounds
    2. Extract the EXACT section names used in the plan (hero, about, portfolio, services, gallery, team, testimonials, etc.)
    3. For each section, determine how many images are needed
    4. Extract relevant keywords for each section from the plan content
    5. Detect the business type from the plan
    6. Calculate total images needed

    Return this JSON structure with ALL detected sections:

    {{
    "total_images_needed": CALCULATED_TOTAL,
    "business_type": "DETECTED_FROM_PLAN",
    "sections": {{
        "EXACT_SECTION_NAME_1": {{
        "count": NUMBER_OF_IMAGES_FOR_THIS_SECTION,
        "keywords": "extracted keywords from plan for this section",
        "description": "brief description of what this section needs"
        }},
        "EXACT_SECTION_NAME_2": {{
        "count": NUMBER_OF_IMAGES_FOR_THIS_SECTION,
        "keywords": "extracted keywords from plan for this section", 
        "description": "brief description of what this section needs"
        }}
        // ... include ALL sections that need images
    }}
    }}

    EXAMPLES of section names to look for:
    - hero, header, banner
    - about, team, story
    - portfolio, projects, work, gallery
    - services, offerings, solutions
    - testimonials, reviews
    - contact, location
    - blog, news
    - features, benefits
    - process, workflow

    IMPORTANT: 
    - Include EVERY section that mentions images/photos/visuals
    - Use the EXACT section name from the plan
    - Don't assume standard sections if they're not mentioned
    - Extract keywords specific to each section's content
    - If a section mentions "7 photos" or "8 images", use that exact count

    Return ONLY the JSON.
    """

            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=parse_prompt)],
                ),
            ]
            
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                contents=contents,
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            
            requirements = json.loads(response.text.strip())
            
            # Log detected sections
            logger.info(f"📋 Dynamic sections detected: {len(requirements['sections'])} sections")
            for section_name, section_data in requirements['sections'].items():
                logger.info(f"   {section_name}: {section_data['count']} images - {section_data['keywords'][:40]}...")
            
            return requirements
            
        except Exception as e:
            logger.error(f"❌ Dynamic section parsing failed: {e}")
            return self._extract_dynamic_fallback_requirements(design_plan)

    def _extract_dynamic_fallback_requirements(self, design_plan: str) -> Dict:
        """Regex ile dynamic fallback parsing (EXISTING - PRESERVED)"""
        import re
        
        requirements = {
            "total_images_needed": 0,
            "business_type": "general",
            "sections": {}
        }
        
        # Business type detection
        business_patterns = {
            'architecture': r'\b(architect|architectural|building|construction)\b',
            'restaurant': r'\b(restaurant|cafe|food|dining|culinary)\b',
            'tech': r'\b(technology|software|app|digital|startup)\b',
            'consulting': r'\b(consulting|advisory|business strategy)\b',
            'fitness': r'\b(fitness|gym|training|workout|sports)\b',
            'healthcare': r'\b(health|medical|clinic|wellness|hospital)\b',
            'education': r'\b(education|school|university|learning)\b',
            'photography': r'\b(photography|photographer|photos|images)\b',
            'law': r'\b(law|legal|lawyer|attorney)\b',
            'finance': r'\b(finance|bank|investment|financial)\b'
        }
        
        for business_type, pattern in business_patterns.items():
            if re.search(pattern, design_plan, re.IGNORECASE):
                requirements["business_type"] = business_type
                break
        
        # Section detection patterns
        section_patterns = {
            # Hero patterns
            r'\b(hero|header|banner)\b.*?(\d+)\s*(image|photo|background)': ('hero', 1),
            r'\b(hero|header|banner)\b(?!.*\d)': ('hero', 1),
            
            # About patterns  
            r'\babout\b.*?(\d+)\s*(image|photo)': ('about', None),
            r'\babout\b(?!.*\d)': ('about', 1),
            
            # Portfolio/Projects patterns
            r'\b(portfolio|projects?|work|gallery)\b.*?(\d+)\s*(image|photo|project)': ('portfolio', None),
            r'\b(portfolio|projects?|work|gallery)\b(?!.*\d)': ('portfolio', 6),
            
            # Services patterns
            r'\bservices?\b.*?(\d+)\s*(image|photo)': ('services', None),
            r'\bservices?\b(?!.*\d)': ('services', 1),
            
            # Team patterns
            r'\bteam\b.*?(\d+)\s*(image|photo|member)': ('team', None),
            r'\bteam\b(?!.*\d)': ('team', 1),
            
            # Testimonials patterns
            r'\btestimonials?\b.*?(\d+)\s*(image|photo)': ('testimonials', None),
            r'\btestimonials?\b(?!.*\d)': ('testimonials', 3),
            
            # Gallery patterns
            r'\bgaller(y|ies)\b.*?(\d+)\s*(image|photo)': ('gallery', None),
            r'\bgaller(y|ies)\b(?!.*\d)': ('gallery', 8),
            
            # Contact patterns
            r'\bcontact\b.*?(\d+)\s*(image|photo)': ('contact', None),
            r'\bcontact\b(?!.*\d)': ('contact', 1),
            
            # Blog patterns
            r'\bblog\b.*?(\d+)\s*(image|photo)': ('blog', None),
            r'\bblog\b(?!.*\d)': ('blog', 4),
            
            # Features patterns
            r'\bfeatures?\b.*?(\d+)\s*(image|photo)': ('features', None),
            r'\bfeatures?\b(?!.*\d)': ('features', 3)
        }
        
        business_type = requirements["business_type"]
        
        for pattern, (section_name, default_count) in section_patterns.items():
            matches = re.finditer(pattern, design_plan, re.IGNORECASE)
            
            for match in matches:
                count = default_count
                if match.groups() and match.group(2) and match.group(2).isdigit():
                    count = int(match.group(2))
                
                # Section-specific keywords
                section_keywords = {
                    'hero': f'{business_type} modern professional workspace background',
                    'about': f'{business_type} team professional portrait story',
                    'portfolio': f'{business_type} project work showcase creative',
                    'services': f'{business_type} service quality offering solution',
                    'team': f'{business_type} team members professional group',
                    'testimonials': f'{business_type} client testimonial review',
                    'gallery': f'{business_type} gallery showcase collection',
                    'contact': f'{business_type} contact office location',
                    'blog': f'{business_type} blog article content',
                    'features': f'{business_type} features benefits solution'
                }
                
                requirements["sections"][section_name] = {
                    "count": count,
                    "keywords": section_keywords.get(section_name, f'{business_type} {section_name} professional'),
                    "description": f"Images for {section_name} section"
                }
        
        # Calculate total
        requirements["total_images_needed"] = sum(
            section_data["count"] for section_data in requirements["sections"].values()
        )
        
        logger.info(f"📋 Fallback detection: {len(requirements['sections'])} sections, {requirements['total_images_needed']} total images")
        
        return requirements


# Singleton instance
context_aware_photo_service = ContextAwarePhotoService()