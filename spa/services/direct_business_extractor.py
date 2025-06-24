# spa/services/direct_business_extractor.py
import json
import logging
from typing import Dict, List, Optional
from google import genai
from google.genai import types
from django.conf import settings

logger = logging.getLogger(__name__)

class DirectBusinessExtractor:
    """
    Orijinal kullanıcı promptundan DOĞRUDAN business context çıkarır
    - Minimal processing
    - Focused extraction
    - High accuracy
    """
    
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        logger.info("🎯 DirectBusinessExtractor initialized")
    
    async def extract_business_context(self, original_prompt: str) -> Dict:
        """
        Orijinal prompttan business context çıkar
        
        Args:
            original_prompt: Kullanıcının yazdığı orijinal prompt
            
        Returns:
            Dict: Business context bilgileri
        """
        logger.info(f"🔍 Extracting business context from: {original_prompt[:100]}...")
        
        try:
            extraction_prompt = f"""
You are a business analysis expert. Extract PRECISE business context from this user prompt.

USER PROMPT:
{original_prompt}

Extract and return this JSON (be SPECIFIC, not generic):

{{
  "business_type": "specific_business_type",
  "industry": "specific_industry", 
  "target_audience": "who_they_serve",
  "main_services": ["service1", "service2", "service3"],
  "business_keywords": ["keyword1", "keyword2", "keyword3", "keyword4"],
  "visual_style": "professional/creative/modern/traditional",
  "sections_needed": {{
    "hero": {{"purpose": "main_attraction", "image_type": "specific_type"}},
    "about": {{"purpose": "company_story", "image_type": "specific_type"}},
    "portfolio": {{"purpose": "work_showcase", "count": 4, "image_type": "specific_type"}},
    "services": {{"purpose": "service_presentation", "image_type": "specific_type"}},
    "contact": {{"purpose": "get_in_touch", "image_type": "specific_type"}}
  }}
}}

EXAMPLES:
- "I'm an architect designing modern homes" → business_type: "architect", industry: "architecture", business_keywords: ["architect", "modern homes", "residential design", "blueprints"]
- "We sell premium organic coffee" → business_type: "coffee_shop", industry: "food_beverage", business_keywords: ["organic coffee", "premium beans", "coffee shop", "barista"]
- "Personal trainer for weight loss" → business_type: "personal_trainer", industry: "fitness", business_keywords: ["personal trainer", "weight loss", "fitness coaching", "gym"]

Be SPECIFIC and ACTIONABLE. Avoid generic terms like "business" or "professional".
"""

            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=extraction_prompt)],
                ),
            ]
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                contents=contents,
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            
            business_context = json.loads(response.text.strip())
            logger.info(f"✅ Business context extracted: {business_context['business_type']}")
            
            # Validation
            if not self._validate_business_context(business_context):
                logger.warning("⚠️ Business context validation failed, using fallback")
                return self._create_fallback_context(original_prompt)
            
            return business_context
            
        except Exception as e:
            logger.error(f"❌ Business context extraction failed: {e}")
            return self._create_fallback_context(original_prompt)
    
    def _validate_business_context(self, context: Dict) -> bool:
        """Business context validation"""
        required_fields = ['business_type', 'industry', 'business_keywords', 'sections_needed']
        
        for field in required_fields:
            if field not in context:
                return False
        
        # business_type should not be generic
        generic_terms = ['business', 'company', 'professional', 'service']
        if context['business_type'].lower() in generic_terms:
            return False
            
        # Should have at least 3 keywords
        if len(context.get('business_keywords', [])) < 3:
            return False
            
        return True
    
    def _create_fallback_context(self, original_prompt: str) -> Dict:
        """Simple fallback context creation"""
        logger.info("🔄 Creating fallback business context")
        
        # Simple keyword extraction
        prompt_lower = original_prompt.lower()
        
        # Business type detection
        business_type = "general_business"
        industry = "general"
        
        if any(word in prompt_lower for word in ['restaurant', 'cafe', 'food', 'cooking']):
            business_type = "restaurant"
            industry = "food_service"
        elif any(word in prompt_lower for word in ['architect', 'design', 'building', 'construction']):
            business_type = "architect"
            industry = "architecture"
        elif any(word in prompt_lower for word in ['fitness', 'gym', 'trainer', 'workout']):
            business_type = "fitness"
            industry = "health_fitness"
        elif any(word in prompt_lower for word in ['lawyer', 'legal', 'law', 'attorney']):
            business_type = "lawyer"
            industry = "legal"
        elif any(word in prompt_lower for word in ['doctor', 'medical', 'clinic', 'health']):
            business_type = "medical"
            industry = "healthcare"
        
        # Extract keywords from prompt
        words = original_prompt.split()
        business_keywords = [word.lower().strip('.,!?') for word in words if len(word) > 3][:6]
        
        return {
            "business_type": business_type,
            "industry": industry,
            "target_audience": "potential_customers",
            "main_services": ["primary_service", "secondary_service"],
            "business_keywords": business_keywords,
            "visual_style": "professional",
            "sections_needed": {
                "hero": {"purpose": "main_attraction", "image_type": f"{business_type}_hero"},
                "about": {"purpose": "company_story", "image_type": f"{business_type}_about"},
                "portfolio": {"purpose": "work_showcase", "count": 4, "image_type": f"{business_type}_work"},
                "services": {"purpose": "service_presentation", "image_type": f"{business_type}_service"},
                "contact": {"purpose": "get_in_touch", "image_type": "office_contact"}
            }
        }

# Singleton instance
_extractor_instance = None

def get_direct_business_extractor():
    """Singleton nesnesini sadece gerektiğinde oluşturur ve döndürür."""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = DirectBusinessExtractor()
    return _extractor_instance
# direct_business_extractor = DirectBusinessExtractor()