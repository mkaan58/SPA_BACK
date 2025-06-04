# spa/services/simple_image_service.py

from google import genai
from django.conf import settings
import json
import logging
import requests
from typing import Dict, List

logger = logging.getLogger(__name__)

class SimpleImageService:
    """Context-aware image service using Unsplash API"""
    
    def __init__(self):
        self.unsplash_access_key = getattr(settings, 'UNSPLASH_ACCESS_KEY', None)
        if not self.unsplash_access_key:
            logger.warning("UNSPLASH_ACCESS_KEY not found in settings")
    
    def get_context_images_for_html(self, prompt: str) -> Dict[str, str]:
        """
        Generate context-aware images for HTML based on prompt
        SYNC VERSION - No async needed
        """
        try:
            # Analyze prompt to determine image needs
            image_context = self._analyze_prompt_for_images(prompt)
            
            # Generate context-aware images
            context_images = {}
            
            for image_type, keywords in image_context.items():
                image_url = self._get_unsplash_image(keywords)
                if image_url:
                    context_images[image_type] = image_url
                else:
                    # Fallback to high-quality placeholder
                    context_images[image_type] = self._get_fallback_image(image_type)
            
            logger.info(f"Generated {len(context_images)} context images")
            return context_images
            
        except Exception as e:
            logger.error(f"Error generating context images: {str(e)}")
            return self._get_default_images()
    
    def _analyze_prompt_for_images(self, prompt: str) -> Dict[str, str]:
        """Analyze prompt to determine what types of images are needed"""
        
        # Initialize base image needs
        image_context = {
            'hero_image': 'professional workspace modern office',
            'about_image': 'professional portrait business person',
            'service_image': 'technology innovation digital',
            'portfolio_1': 'creative project design work',
            'portfolio_2': 'development coding programming',
            'portfolio_3': 'business solution strategy'
        }
        
        prompt_lower = prompt.lower()
        
        # Smart keyword detection for different business types
        if any(word in prompt_lower for word in ['restaurant', 'food', 'cafe', 'dining', 'menu']):
            image_context.update({
                'hero_image': 'restaurant interior dining modern',
                'about_image': 'chef cooking professional kitchen',
                'service_image': 'delicious food plating gourmet',
                'portfolio_1': 'restaurant food photography',
                'portfolio_2': 'kitchen cooking preparation',
                'portfolio_3': 'dining experience atmosphere'
            })
        
        elif any(word in prompt_lower for word in ['fitness', 'gym', 'workout', 'health', 'training']):
            image_context.update({
                'hero_image': 'modern gym fitness equipment',
                'about_image': 'fitness trainer professional',
                'service_image': 'workout training session',
                'portfolio_1': 'fitness transformation success',
                'portfolio_2': 'gym equipment modern facility',
                'portfolio_3': 'group fitness class training'
            })
        
        elif any(word in prompt_lower for word in ['photography', 'photo', 'camera', 'portrait']):
            image_context.update({
                'hero_image': 'photography studio professional lighting',
                'about_image': 'photographer with camera professional',
                'service_image': 'camera photography equipment',
                'portfolio_1': 'portrait photography professional',
                'portfolio_2': 'wedding photography beautiful',
                'portfolio_3': 'landscape photography stunning'
            })
        
        elif any(word in prompt_lower for word in ['law', 'lawyer', 'legal', 'attorney', 'justice']):
            image_context.update({
                'hero_image': 'law office professional modern',
                'about_image': 'lawyer professional business suit',
                'service_image': 'legal documents justice scale',
                'portfolio_1': 'courtroom legal professional',
                'portfolio_2': 'legal consultation meeting',
                'portfolio_3': 'law books legal research'
            })
        
        elif any(word in prompt_lower for word in ['medical', 'doctor', 'health', 'clinic', 'hospital']):
            image_context.update({
                'hero_image': 'medical clinic modern healthcare',
                'about_image': 'doctor professional healthcare',
                'service_image': 'medical equipment healthcare',
                'portfolio_1': 'medical consultation patient care',
                'portfolio_2': 'healthcare technology modern',
                'portfolio_3': 'medical team professionals'
            })
        
        elif any(word in prompt_lower for word in ['real estate', 'property', 'home', 'house', 'realtor']):
            image_context.update({
                'hero_image': 'luxury home real estate modern',
                'about_image': 'real estate agent professional',
                'service_image': 'beautiful home interior design',
                'portfolio_1': 'luxury property exterior',
                'portfolio_2': 'modern home interior',
                'portfolio_3': 'property investment success'
            })
        
        elif any(word in prompt_lower for word in ['wedding', 'event', 'planning', 'celebration']):
            image_context.update({
                'hero_image': 'elegant wedding venue decoration',
                'about_image': 'event planner professional',
                'service_image': 'wedding decoration beautiful',
                'portfolio_1': 'wedding ceremony beautiful',
                'portfolio_2': 'event decoration elegant',
                'portfolio_3': 'celebration party planning'
            })
        
        elif any(word in prompt_lower for word in ['travel', 'tourism', 'vacation', 'adventure']):
            image_context.update({
                'hero_image': 'travel destination beautiful landscape',
                'about_image': 'travel guide professional',
                'service_image': 'adventure travel experience',
                'portfolio_1': 'travel destination exotic',
                'portfolio_2': 'adventure activity exciting',
                'portfolio_3': 'cultural experience travel'
            })
        
        elif any(word in prompt_lower for word in ['fashion', 'style', 'clothing', 'design']):
            image_context.update({
                'hero_image': 'fashion design studio modern',
                'about_image': 'fashion designer professional',
                'service_image': 'fashion clothing elegant',
                'portfolio_1': 'fashion design collection',
                'portfolio_2': 'clothing style modern',
                'portfolio_3': 'fashion photography model'
            })
        
        return image_context

    def get_truly_dynamic_images(self, prompt: str, design_plan: str) -> Dict[str, str]:
        """
        Gerçekten dinamik resim üretimi - kullanıcının istediği sayıda
        """
        try:
            # Design plan'dan image plan'ını çıkar
            image_plan = self._extract_image_plan(design_plan)
            
            if not image_plan:
                # Fallback: prompt'tan sayı çıkarmaya çalış
                image_plan = self._analyze_prompt_for_count(prompt)
            
            # Dynamic resim üretimi
            return self._generate_exact_count_images(image_plan, prompt)
            
        except Exception as e:
            logger.error(f"Dynamic image generation failed: {e}")
            # Son çare: En az 2 resim
            return self._get_minimal_fallback()

    def _extract_image_plan(self, design_plan: str) -> dict:
        """Design plan'dan JSON çıkar"""
        import re
        import json
        
        # JSON'u bul ve parse et
        json_patterns = [
            r'"total_images_needed":\s*(\d+)',  # Sayı yakala
            r'\{[^}]*"total_images_needed"[^}]*\}',  # JSON yakala
            r'IMAGE PLAN JSON:\s*(\{.*?\})'  # JSON block yakala
        ]
        
        for pattern in json_patterns:
            match = re.search(pattern, design_plan, re.DOTALL)
            if match:
                try:
                    if 'total_images_needed' in match.group(0):
                        json_text = match.group(0)
                        return json.loads(json_text)
                except:
                    continue
        
        return None

    def _analyze_prompt_for_count(self, prompt: str) -> dict:
        """Prompt'tan sayı çıkar - GERÇEK DİNAMİK"""
        import re
        
        # Sayı bulma patterns
        number_patterns = [
            r'(\d+)\s*(?:resim|image|photo|görsel)',
            r'(\d+)\s*(?:tane|adet)',
            r'(\d+)\s*(?:pictures|pics)'
        ]
        
        total_count = 6  # Default
        
        for pattern in number_patterns:
            match = re.search(pattern, prompt.lower())
            if match:
                total_count = int(match.group(1))
                break
        
        # Özel kelimeler
        if any(word in prompt.lower() for word in ['gallery', 'galeri']):
            total_count = max(total_count, 8)
        elif any(word in prompt.lower() for word in ['minimal', 'simple', 'basit']):
            total_count = min(total_count, 4)
        
        # Section dağılımı - DYNAMIC
        return self._distribute_images_dynamically(total_count, prompt)

    def _distribute_images_dynamically(self, total_count: int, prompt: str) -> dict:
        """Toplam sayıyı section'lara dinamik dağıt"""
        
        # Business type analizi
        business_type = self._detect_business_type(prompt)
        
        # Dinamik dağılım kuralları
        if total_count <= 3:
            sections = {
                "hero": {"count": 1, "keywords": f"{business_type} professional"},
                "about": {"count": 1, "keywords": "professional portrait"},
                "portfolio": {"count": total_count - 2, "keywords": f"{business_type} work"}
            }
        elif total_count <= 6:
            sections = {
                "hero": {"count": 1, "keywords": f"{business_type} workspace"},
                "about": {"count": 1, "keywords": "professional portrait"},
                "portfolio": {"count": total_count - 3, "keywords": f"{business_type} projects"},
                "services": {"count": 1, "keywords": f"{business_type} services"}
            }
        else:
            # 7+ resim için
            portfolio_count = max(total_count - 4, 3)
            sections = {
                "hero": {"count": 1, "keywords": f"{business_type} modern"},
                "about": {"count": 1, "keywords": "professional portrait"},
                "portfolio": {"count": portfolio_count, "keywords": f"{business_type} showcase"},
                "services": {"count": 1, "keywords": f"{business_type} solutions"},
                "gallery": {"count": total_count - portfolio_count - 3, "keywords": f"{business_type} gallery"}
            }
        
        return {
            "total_images_needed": total_count,
            "sections": sections
        }

    def _generate_exact_count_images(self, image_plan: dict, prompt: str) -> Dict[str, str]:
        """Exact sayıda resim üret"""
        
        context_images = {}
        sections = image_plan.get("sections", {})
        
        for section_name, section_info in sections.items():
            count = section_info.get("count", 0)
            keywords = section_info.get("keywords", "professional business")
            
            if count == 0:
                continue
                
            # Bu section için tam sayıda resim üret
            for i in range(count):
                if count == 1:
                    key = f"{section_name}_image"
                else:
                    key = f"{section_name}_{i+1}"
                
                # Unsplash'ten çek
                image_url = self._get_unsplash_image(keywords)
                context_images[key] = image_url or f"https://picsum.photos/800/600?random={len(context_images)+1}"
        
        logger.info(f"✅ Generated EXACTLY {len(context_images)} images as requested")
        return context_images
    
    def _get_unsplash_image(self, keywords: str, width: int = 800, height: int = 600) -> str:
        """Get image from Unsplash API based on keywords"""
        
        if not self.unsplash_access_key:
            return None
        
        try:
            # Unsplash API endpoint
            url = "https://api.unsplash.com/search/photos"
            
            params = {
                'query': keywords,
                'per_page': 1,
                'page': 1,
                'orientation': 'landscape',
                'order_by': 'relevant'
            }
            
            headers = {
                'Authorization': f'Client-ID {self.unsplash_access_key}'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results') and len(data['results']) > 0:
                    photo = data['results'][0]
                    # Get optimized URL
                    image_url = photo['urls']['regular']
                    # Add optimization parameters
                    optimized_url = f"{image_url}&w={width}&h={height}&fit=crop&crop=center"
                    return optimized_url
            
            logger.warning(f"Failed to get Unsplash image for keywords: {keywords}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching Unsplash image: {str(e)}")
            return None
    
    def _get_fallback_image(self, image_type: str) -> str:
        """Get high-quality fallback image based on type"""
        
        fallback_mapping = {
            'hero_image': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200&h=600&fit=crop&crop=center',  # Modern office
            'about_image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=center',  # Professional person
            'service_image': 'https://images.unsplash.com/photo-1551434678-e076c223a692?w=800&h=500&fit=crop&crop=center',  # Technology
            'portfolio_1': 'https://images.unsplash.com/photo-1467232004584-a241de8bcf5d?w=600&h=400&fit=crop&crop=center',  # Creative work
            'portfolio_2': 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=600&h=400&fit=crop&crop=center',  # Development
            'portfolio_3': 'https://images.unsplash.com/photo-1553877522-43269d4ea984?w=600&h=400&fit=crop&crop=center'   # Business
        }
        
        return fallback_mapping.get(image_type, 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800&h=600&fit=crop&crop=center')
    
    def _get_default_images(self) -> Dict[str, str]:
        """Get default high-quality images as last resort"""
        
        return {
            'hero_image': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200&h=600&fit=crop&crop=center',
            'about_image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=center',
            'service_image': 'https://images.unsplash.com/photo-1551434678-e076c223a692?w=800&h=500&fit=crop&crop=center',
            'portfolio_1': 'https://images.unsplash.com/photo-1467232004584-a241de8bcf5d?w=600&h=400&fit=crop&crop=center',
            'portfolio_2': 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=600&h=400&fit=crop&crop=center',
            'portfolio_3': 'https://images.unsplash.com/photo-1553877522-43269d4ea984?w=600&h=400&fit=crop&crop=center'
        }

    def _detect_business_type(self, prompt: str) -> str:
        """Prompt'tan business type'ını tespit et"""
        prompt_lower = prompt.lower()
        
        business_keywords = {
            'restaurant': ['restaurant', 'cafe', 'food', 'dining', 'menu', 'chef', 'cooking'],
            'fitness': ['fitness', 'gym', 'workout', 'health', 'training', 'exercise'],
            'photography': ['photography', 'photo', 'camera', 'portrait', 'wedding photo'],
            'law': ['law', 'lawyer', 'legal', 'attorney', 'justice', 'court'],
            'medical': ['medical', 'doctor', 'health', 'clinic', 'hospital', 'healthcare'],
            'real estate': ['real estate', 'property', 'home', 'house', 'realtor'],
            'wedding': ['wedding', 'event planning', 'celebration', 'party'],
            'travel': ['travel', 'tourism', 'vacation', 'adventure', 'trip'],
            'fashion': ['fashion', 'style', 'clothing', 'design', 'boutique'],
            'technology': ['technology', 'software', 'app', 'digital', 'tech', 'development'],
            'consulting': ['consulting', 'advisory', 'business', 'strategy'],
            'creative': ['design', 'creative', 'art', 'graphic', 'marketing']
        }
        
        for business_type, keywords in business_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                return business_type
        
        return 'professional business'

    def _get_minimal_fallback(self) -> Dict[str, str]:
        """Minimal fallback - en az resim sayısı"""
        return {
            'hero_image': self._get_unsplash_image('professional modern workspace') or 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200&h=600&fit=crop',
            'about_image': self._get_unsplash_image('professional portrait business') or 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop'
        }