# spa/services/robust_image_service.py
import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.core.cache import cache
from spa.services.mcp_photo_client import mcp_photo_client
from spa.services.simple_image_service import SimpleImageService

logger = logging.getLogger(__name__)

class RobustImageService:
    """
    Çoklu katmanlı hata yönetimi ile fotoğraf servisi
    MCP -> Unsplash -> Picsum -> Cache fallback zinciri
    """
    
    def __init__(self):
        self.mcp_client = mcp_photo_client
        self.unsplash_service = SimpleImageService()
        self.max_retries = 3
        self.timeout_seconds = 30
        self.cache_timeout = 3600  # 1 saat
        
    async def get_context_images_with_fallback(
        self, 
        prompt: str, 
        design_plan: str = "", 
        user_preferences: Dict = None
    ) -> Dict:
        """
        Çoklu katmanlı fallback sistemi ile fotoğraf getirme
        """
        
        cache_key = self._generate_cache_key(prompt, design_plan, user_preferences)
        
        # 1. Cache kontrolü
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info("📦 Returning cached images")
            return cached_result
        
        # 2. MCP öncelikli deneme
        try:
            logger.info("🚀 Attempting MCP context-aware generation...")
            images = await self._try_mcp_generation(prompt, design_plan, user_preferences)
            if self._validate_image_urls(images):
                cache.set(cache_key, images, self.cache_timeout)
                logger.info("✅ MCP generation successful")
                return images
        except Exception as e:
            logger.warning(f"⚠️ MCP failed: {e}")
        
        # 3. Unsplash fallback
        try:
            logger.info("🔄 Falling back to Unsplash...")
            images = await self._try_unsplash_generation(prompt)
            if self._validate_image_urls(images):
                cache.set(cache_key, images, self.cache_timeout)
                logger.info("✅ Unsplash fallback successful")
                return images
        except Exception as e:
            logger.warning(f"⚠️ Unsplash failed: {e}")
        
        # 4. Picsum son çare
        logger.warning("🆘 Using Picsum placeholder fallback")
        images = self._get_picsum_fallback()
        cache.set(cache_key, images, self.cache_timeout)
        return images
    
    async def _try_mcp_generation(self, prompt: str, design_plan: str, user_preferences: Dict) -> Dict:
        """MCP ile context-aware generation dene"""
        
        # Timeout ile MCP çağrısı
        try:
            images = await asyncio.wait_for(
                self.mcp_client.get_context_aware_photos(
                    design_plan=design_plan,
                    user_preferences=user_preferences or {},
                    section_requirements=self._extract_sections(design_plan)
                ),
                timeout=self.timeout_seconds
            )
            return images
        except asyncio.TimeoutError:
            raise Exception("MCP request timeout")
        except Exception as e:
            await self._handle_mcp_connection_error()
            raise Exception(f"MCP generation failed: {e}")
    
    async def _try_unsplash_generation(self, prompt: str) -> Dict:
        """Unsplash API ile basit generation dene"""
        try:
            # Sync fonksiyonu async'e çevir
            from asgiref.sync import sync_to_async
            images = await sync_to_async(self.unsplash_service.get_context_images_for_html)(prompt)
            return images
        except Exception as e:
            raise Exception(f"Unsplash generation failed: {e}")
    
    async def _handle_mcp_connection_error(self):
        """MCP bağlantı hatası durumunda temizlik"""
        try:
            if self.mcp_client.is_connected:
                await self.mcp_client.disconnect()
                logger.info("🔌 MCP connection reset")
        except Exception as e:
            logger.error(f"MCP cleanup error: {e}")
    
    def _validate_image_urls(self, images: Dict) -> bool:
        """Fotoğraf URL'lerinin geçerliliğini kontrol et"""
        if not images or not isinstance(images, dict):
            return False
        
        required_keys = ['hero_image', 'about_image', 'portfolio_1']
        valid_urls = 0
        
        for key in required_keys:
            url = images.get(key)
            if url and isinstance(url, str) and url.startswith(('http://', 'https://')):
                valid_urls += 1
        
        # En az 2 geçerli URL olmalı
        return valid_urls >= 2
    
    def _generate_cache_key(self, prompt: str, design_plan: str, user_preferences: Dict) -> str:
        """Cache key oluştur"""
        import hashlib
        
        # Key bileşenlerini birleştir
        key_components = [
            prompt[:100],  # İlk 100 karakter
            str(user_preferences.get('theme', 'light')),
            str(user_preferences.get('primary_color', '')),
            str(user_preferences.get('business_type', ''))
        ]
        
        key_string = '|'.join(key_components)
        return f"context_images_{hashlib.md5(key_string.encode()).hexdigest()}"
    
    def _extract_sections(self, design_plan: str) -> List[Dict]:
        """Tasarım planından bölümleri çıkar"""
        sections = []
        
        section_map = {
            'hero': {'purpose': 'main attraction', 'mood': 'inspiring'},
            'about': {'purpose': 'personal connection', 'mood': 'authentic'},
            'portfolio': {'purpose': 'showcase work', 'mood': 'professional'},
            'services': {'purpose': 'service presentation', 'mood': 'clean'},
            'contact': {'purpose': 'accessibility', 'mood': 'welcoming'},
            'testimonials': {'purpose': 'social proof', 'mood': 'trustworthy'},
            'team': {'purpose': 'human connection', 'mood': 'friendly'}
        }
        
        design_plan_lower = design_plan.lower()
        
        for section_name, properties in section_map.items():
            if section_name in design_plan_lower:
                sections.append({
                    'section_name': section_name,
                    'image_purpose': properties['purpose'],
                    'required_mood': properties['mood'],
                    'dimensions': self._get_section_dimensions(section_name)
                })
        
        return sections
    
    def _get_section_dimensions(self, section_name: str) -> str:
        """Bölüm için ideal boyutları döndür"""
        dimensions_map = {
            'hero': '1920x1080',
            'about': '400x400',
            'portfolio': '600x400',
            'services': '800x500',
            'contact': '600x300',
            'testimonials': '300x300',
            'team': '350x350'
        }
        return dimensions_map.get(section_name, '600x400')
    
    def _get_picsum_fallback(self) -> Dict:
        """Son çare Picsum placeholder'ları"""
        return {
            'hero_image': 'https://picsum.photos/1200/600?random=1',
            'about_image': 'https://picsum.photos/400/400?random=2',
            'portfolio_1': 'https://picsum.photos/600/400?random=3',
            'portfolio_2': 'https://picsum.photos/600/400?random=4',
            'portfolio_3': 'https://picsum.photos/600/400?random=5',
            'service_image': 'https://picsum.photos/800/500?random=6',
            'contact_image': 'https://picsum.photos/600/300?random=7',
            'testimonial_image': 'https://picsum.photos/300/300?random=8'
        }

# Health Check Sistemi
class MCPHealthChecker:
    """MCP servisinin sağlığını kontrol eden sistem"""
    
    def __init__(self):
        self.last_check_time = 0
        self.check_interval = 300  # 5 dakika
        self.is_healthy = True
    
    async def check_mcp_health(self) -> bool:
        """MCP servisinin sağlığını kontrol et"""
        current_time = time.time()
        
        # Son kontrolden 5 dakika geçmemişse cached sonucu döndür
        if current_time - self.last_check_time < self.check_interval:
            return self.is_healthy
        
        try:
            # Basit bir test isteği gönder
            if not mcp_photo_client.is_connected:
                await mcp_photo_client.connect()
            
            # Test parametreleri
            test_params = {
                "design_plan": "Simple test website",
                "user_preferences": {"theme": "light", "primary_color": "#4B5EAA"},
                "section_requirements": []
            }
            
            # Timeout ile test
            await asyncio.wait_for(
                mcp_photo_client.get_context_aware_photos(**test_params),
                timeout=10
            )
            
            self.is_healthy = True
            logger.info("✅ MCP health check passed")
            
        except Exception as e:
            self.is_healthy = False
            logger.warning(f"❌ MCP health check failed: {e}")
        
        self.last_check_time = current_time
        return self.is_healthy

# Circuit Breaker Pattern
class MCPCircuitBreaker:
    """MCP için circuit breaker pattern implementasyonu"""
    
    def __init__(self, failure_threshold=5, recovery_timeout=300):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    async def call_with_circuit_breaker(self, func, *args, **kwargs):
        """Circuit breaker ile fonksiyon çağrısı"""
        
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'HALF_OPEN'
                logger.info("🔄 Circuit breaker: HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            
            # Başarılı çağrı
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failure_count = 0
                logger.info("✅ Circuit breaker: CLOSED state")
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
                logger.warning(f"🔴 Circuit breaker: OPEN state (failures: {self.failure_count})")
            
            raise e

# Singleton instances
robust_image_service = RobustImageService()
mcp_health_checker = MCPHealthChecker()
mcp_circuit_breaker = MCPCircuitBreaker()

