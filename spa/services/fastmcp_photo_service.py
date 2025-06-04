# spa/services/fastmcp_photo_service.py
import os
import asyncio
import logging
from dataclasses import dataclass
from typing import Optional, List, Dict, Union
import httpx
from dotenv import load_dotenv
from django.conf import settings

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
    FastMCP tabanlı context-aware fotoğraf servisi
    İçerik bazlı akıllı resim seçimi yapar
    """
    
    def __init__(self):
        self.access_key = getattr(settings, 'UNSPLASH_ACCESS_KEY', None) or os.getenv("UNSPLASH_ACCESS_KEY")
        if not self.access_key:
            logger.error("❌ UNSPLASH_ACCESS_KEY not found!")
            raise ValueError("Missing UNSPLASH_ACCESS_KEY")
        
        logger.info("✅ ContextAwarePhotoService initialized")
    
    async def search_photos(
        self,
        query: str,
        page: Union[int, str] = 1,
        per_page: Union[int, str] = 10,
        order_by: str = "relevant",
        color: Optional[str] = None,
        orientation: Optional[str] = None
    ) -> List[UnsplashPhoto]:
        """
        Unsplash'ten fotoğraf ara - FastMCP tarzı
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
    
    async def get_context_aware_photos(
        self,
        design_plan: str,
        user_preferences: Dict,
        section_requirements: List[Dict] = None
    ) -> Dict[str, str]:
        """
        Context-aware fotoğrafları getir - ANA FONKSİYON
        """
        logger.info("🚀 Starting context-aware photo generation...")
        
        business_type = self._extract_business_type(design_plan, user_preferences)
        theme = user_preferences.get('theme', 'light')
        
        logger.info(f"📊 Detected business type: {business_type}, theme: {theme}")
        
        # Section-based photo generation
        section_photos = {}
        
        # Hero section
        hero_query = self._generate_hero_query(business_type, user_preferences)
        hero_photos = await self.search_photos(
            query=hero_query,
            per_page=5,
            orientation="landscape"
        )
        if hero_photos:
            raw_url = hero_photos[0].urls['regular']
            optimized_url = f"{raw_url}&w=1200&h=600&fit=crop&crop=center"
            section_photos['hero_image'] = optimized_url
            logger.info(f"✅ Hero image: {hero_query}")
        
        # About section
        about_query = self._generate_about_query(business_type)
        about_photos = await self.search_photos(
            query=about_query,
            per_page=3,
            orientation="portrait"
        )
        if about_photos:
            section_photos['about_image'] = about_photos[0].urls['regular']
            logger.info(f"✅ About image: {about_query}")
        
        # Portfolio section - 3 farklı query
        portfolio_queries = self._generate_portfolio_queries(business_type)
        for i, portfolio_query in enumerate(portfolio_queries[:3], 1):
            portfolio_photos = await self.search_photos(
                query=portfolio_query,
                per_page=3,
                orientation="landscape"
            )
            if portfolio_photos:
                section_photos[f'portfolio_{i}'] = portfolio_photos[0].urls['regular']
                logger.info(f"✅ Portfolio {i}: {portfolio_query}")
        
        # Service section
        service_query = self._generate_service_query(business_type)
        service_photos = await self.search_photos(
            query=service_query,
            per_page=3,
            orientation="landscape"
        )
        if service_photos:
            section_photos['service_image'] = service_photos[0].urls['regular']
            logger.info(f"✅ Service image: {service_query}")
        
        logger.info(f"🎉 Generated {len(section_photos)} context-aware photos")
        return section_photos
    
    def _extract_business_type(self, design_plan: str, user_preferences: Dict) -> str:
        """Business type'ını extract et"""
        
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
    
    def _generate_hero_query(self, business_type: str, user_preferences: Dict) -> str:
        """Hero section için query oluştur"""
        
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
        """About section için query oluştur"""
        
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
        """Portfolio section için 3 farklı query oluştur"""
        
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
        """Service section için query oluştur"""
        
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


# Singleton instance
context_aware_photo_service = ContextAwarePhotoService()