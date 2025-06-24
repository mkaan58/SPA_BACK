# spa/services/focused_query_generator.py
import logging
import json
from typing import Dict, List
from google import genai
from google.genai import types
from django.conf import settings

logger = logging.getLogger(__name__)

class FocusedQueryGenerator:
    """
    AI-Powered Query Generator
    Yapay zeka ile business context'ten optimal photo queries üretir
    """
    
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        logger.info("🧠 AI-Powered FocusedQueryGenerator initialized")
    
    def generate_section_queries(self, business_context: Dict, original_prompt: str) -> Dict[str, List[str]]:
        """
        AI ile business context'ten optimal queries üret
        
        Args:
            business_context: Business context bilgileri
            original_prompt: Orijinal kullanıcı promptu
            
        Returns:
            Dict: Section bazında query listesi
        """
        business_keywords = business_context.get('business_keywords', [])
        business_type = business_context.get('business_type', 'business')
        sections_needed = business_context.get('sections_needed', {})
        
        logger.info(f"🎯 AI generating queries for: {business_type}")
        
        try:
            # AI'ya query generation yaptır
            ai_queries = self._generate_ai_queries(
                business_context, original_prompt, sections_needed
            )
            
            # AI sonucunu parse et
            section_queries = self._parse_ai_queries(ai_queries, sections_needed)
            
            logger.info(f"✅ AI generated queries for {len(section_queries)} sections")
            return section_queries
            
        except Exception as e:
            logger.error(f"❌ AI query generation failed: {e}")
            # Fallback: basit keyword kullan
            return self._fallback_queries(business_context, sections_needed)
    
    def _generate_ai_queries(self, business_context: Dict, original_prompt: str, sections_needed: Dict) -> Dict:
        """AI ile query generation"""
        
        # Sections'ları dinamik olarak hazırla
        dynamic_sections = {}
        for section_name, section_info in sections_needed.items():
            count = section_info.get('count', 1)
            dynamic_sections[section_name] = {
                "count": count,
                "purpose": section_info.get('purpose', f'{section_name} section'),
                "image_type": section_info.get('image_type', f'{section_name} image')
            }
        
        query_prompt = f"""
You are a photo search expert. Generate OPTIMAL photo search queries for Unsplash API.

BUSINESS CONTEXT:
Business Type: {business_context.get('business_type', 'business')}
Industry: {business_context.get('industry', 'general')}
Keywords: {business_context.get('business_keywords', [])}

ORIGINAL USER PROMPT:
{original_prompt}

DYNAMIC SECTIONS DETECTED:
{json.dumps(dynamic_sections, indent=2)}

GENERATE photo search queries with these STRICT RULES:

1. MAXIMUM 2-3 words per query
2. NO generic words like "professional", "modern", "business"
3. USE specific business keywords from context
4. DIFFERENT queries for each section based on section PURPOSE
5. FOCUS on visual elements that would appear in photos
6. Generate EXACTLY the number of queries specified in "count" for each section

EXAMPLES:
- Curtain business → "luxury curtains", "window drapes", "fabric textures"
- Restaurant → "gourmet food", "chef cooking", "restaurant interior"
- Fitness → "gym equipment", "workout session", "fitness training"

Return this JSON format (use EXACT section names from DYNAMIC SECTIONS):
{{"""

        # Dinamik JSON formatını oluştur
        for section_name, section_info in dynamic_sections.items():
            count = section_info['count']
            if count > 1:
                query_prompt += f'\n  "{section_name}": ["query1", "query2", ..., "query{count}"],'
            else:
                query_prompt += f'\n  "{section_name}": ["query1"],'
        
        query_prompt = query_prompt.rstrip(',') + '\n}'
        
        query_prompt += f"""

CRITICAL: 
- Each query should be 1-3 words ONLY
- Queries should be VISUALLY SPECIFIC to the business
- NO abstract concepts, only concrete visual elements
- Use business keywords directly when possible
- Generate queries that match the PURPOSE of each section:
  * Hero sections: Main business visual representation
  * About sections: Professional/personal representation
  * Portfolio sections: Work examples, products, results
  * Services sections: Service delivery, tools, process
  * Gallery sections: Multiple examples of work
  * Contact sections: Location, office, accessibility
- ADAPT to the actual business type and prompt content
"""

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=query_prompt)],
            ),
        ]
        
        response = self.client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",
            contents=contents,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        
        return json.loads(response.text.strip())
    
    def _parse_ai_queries(self, ai_queries: Dict, sections_needed: Dict) -> Dict[str, List[str]]:
        """AI query sonuçlarını parse et"""
        
        parsed_queries = {}
        
        for section_name, section_info in sections_needed.items():
            count = section_info.get('count', 1)
            ai_section_queries = ai_queries.get(section_name, [])
            
            if count > 1:
                # Multiple queries needed (portfolio)
                queries = []
                for i in range(count):
                    if i < len(ai_section_queries):
                        query = ai_section_queries[i]
                    else:
                        # Fallback: re-use existing queries
                        query = ai_section_queries[i % len(ai_section_queries)] if ai_section_queries else "business work"
                    
                    # Optimize query
                    optimized = self._optimize_query(query)
                    queries.append(optimized)
                
                parsed_queries[section_name] = queries
            else:
                # Single query
                query = ai_section_queries[0] if ai_section_queries else "business professional"
                optimized = self._optimize_query(query)
                parsed_queries[section_name] = [optimized]
        
        # Log generated queries
        for section, queries in parsed_queries.items():
            logger.info(f"🎯 AI {section}: {queries}")
        
        return parsed_queries
    
    def _fallback_queries(self, business_context: Dict, sections_needed: Dict) -> Dict[str, List[str]]:
        """AI başarısız olursa fallback queries"""
        
        logger.info("🔄 Using fallback query generation")
        
        business_keywords = business_context.get('business_keywords', [])
        main_keyword = business_keywords[0] if business_keywords else business_context.get('business_type', 'business')
        
        # Ana keyword'den ilk 1-2 kelimeyi al
        main_words = main_keyword.split()[:2]
        main_query = ' '.join(main_words)
        
        fallback_queries = {}
        
        for section_name, section_info in sections_needed.items():
            count = section_info.get('count', 1)
            
            if count > 1:
                # Portfolio için farklı keywords kullan
                queries = []
                for i in range(count):
                    if i < len(business_keywords):
                        keyword_words = business_keywords[i].split()[:2]
                        query = ' '.join(keyword_words)
                    else:
                        query = main_query
                    queries.append(query)
                fallback_queries[section_name] = queries
            else:
                # Single query
                fallback_queries[section_name] = [main_query]
        
        return fallback_queries
    
    def _optimize_query(self, query: str) -> str:
        """Query'i optimize et"""
        if not query:
            return "business"
        
        words = query.split()
        
        # Maximum 3 kelime
        if len(words) > 3:
            words = words[:3]
        
        # Gereksiz kelimeleri çıkar
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'professional', 'modern', 'business'}
        filtered_words = [word for word in words if word.lower() not in stop_words]
        
        # En az 1 kelime olsun
        if not filtered_words:
            filtered_words = words[:2]
        
        result = ' '.join(filtered_words)
        return result if result else "business"

# Singleton instance
_query_generator_instance = None

def get_focused_query_generator():
    global _query_generator_instance
    if _query_generator_instance is None:
        _query_generator_instance = FocusedQueryGenerator()
    return _query_generator_instance

# focused_query_generator = FocusedQueryGenerator()