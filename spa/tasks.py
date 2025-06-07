# # spa/tasks.py - Fixed version (no nested tasks, no emojis)
# from celery import shared_task
# from celery.utils.log import get_task_logger
# from django.conf import settings
# from google import genai
# from google.genai import types
# import json
# import asyncio
# from typing import Dict, List
# from spa.models import Website, WebsiteDesignPlan
# from spa.services.simple_image_service import SimpleImageService
# from spa.utils.color_utils import ColorHarmonySystem
# from spa.api.approve_plan_prompt import generate_enhanced_prompt
# import time

# logger = get_task_logger(__name__)

# # FastMCP service import (optional)
# try:
#     from spa.services.fastmcp_photo_service import context_aware_photo_service
#     FASTMCP_AVAILABLE = True
# except ImportError:
#     FASTMCP_AVAILABLE = False
#     logger.warning("FastMCP service not available")

# @shared_task(bind=True, max_retries=3)
# def generate_context_aware_images_task(self, design_plan_text, user_preferences, business_type):
#     """
#     Celery task for generating context-aware images asynchronously
#     """
#     logger.info(f"Starting async image generation for business type: {business_type}")
    
#     try:
#         # Initialize services
#         simple_service = SimpleImageService()
        
#         # Try different image generation strategies
#         context_images = {}
#         generation_method = "UNKNOWN"
        
#         # 1. FastMCP Context-Aware (if available)
#         if FASTMCP_AVAILABLE and getattr(settings, 'USE_FASTMCP_PHOTO_SERVICE', True):
#             try:
#                 logger.info("Attempting FastMCP context-aware generation...")
                
#                 # Since we're in Celery, we need to handle async properly
#                 loop = asyncio.new_event_loop()
#                 asyncio.set_event_loop(loop)
                
#                 context_images = loop.run_until_complete(
#                     context_aware_photo_service.get_context_aware_photos_with_verification(
#                         design_plan=design_plan_text,
#                         user_preferences=user_preferences,
#                         section_requirements=[]
#                     )
#                 )
                
#                 if context_images and len(context_images) >= 3:
#                     generation_method = "FASTMCP_CONTEXT_AWARE"
#                     logger.info(f"FastMCP success: {len(context_images)} images")
#                 else:
#                     raise Exception("FastMCP returned insufficient images")
                    
#             except Exception as fastmcp_error:
#                 logger.warning(f"FastMCP failed: {fastmcp_error}")
#                 context_images = {}
        
#         # 2. Enhanced Dynamic Generation (Fallback 1)
#         if not context_images:
#             try:
#                 logger.info("Falling back to enhanced dynamic generation...")
                
#                 # Parse business requirements from design plan
#                 requirements = _parse_business_requirements(design_plan_text, business_type)
#                 context_images = _generate_dynamic_business_images(requirements, user_preferences)
                
#                 if context_images and len(context_images) >= 3:
#                     generation_method = "ENHANCED_DYNAMIC"
#                     logger.info(f"Enhanced dynamic success: {len(context_images)} images")
#                 else:
#                     raise Exception("Enhanced dynamic generation failed")
                    
#             except Exception as enhanced_error:
#                 logger.warning(f"Enhanced dynamic failed: {enhanced_error}")
#                 context_images = {}
        
#         # 3. Context-Aware Unsplash (Fallback 2)
#         if not context_images:
#             try:
#                 logger.info("Falling back to context-aware Unsplash...")
#                 context_images = simple_service.get_context_images_for_html(design_plan_text)
                
#                 if context_images and len(context_images) >= 3:
#                     generation_method = "CONTEXT_AWARE_UNSPLASH"
#                     logger.info(f"Context-aware Unsplash success: {len(context_images)} images")
#                 else:
#                     raise Exception("Context-aware Unsplash failed")
                    
#             except Exception as context_error:
#                 logger.warning(f"Context-aware Unsplash failed: {context_error}")
#                 context_images = {}
        
#         # 4. Emergency High-Quality Fallback
#         if not context_images:
#             logger.info("Using emergency high-quality fallback...")
#             context_images = _get_emergency_business_images(business_type, design_plan_text)
#             generation_method = "EMERGENCY_FALLBACK"
        
#         # Validate final result
#         if not context_images or len(context_images) < 2:
#             raise Exception(f"Image generation completely failed. Got {len(context_images)} images")
        
#         logger.info(f"Task completed: {len(context_images)} images via {generation_method}")
        
#         return {
#             'success': True,
#             'context_images': context_images,
#             'generation_method': generation_method,
#             'image_count': len(context_images),
#             'business_type': business_type
#         }
        
#     except Exception as e:
#         logger.error(f"Image generation task failed: {str(e)}")
        
#         # Retry logic
#         if self.request.retries < self.max_retries:
#             logger.info(f"Retrying task, attempt {self.request.retries + 1}/{self.max_retries}")
#             raise self.retry(countdown=60 * (self.request.retries + 1))
        
#         # Final fallback if all retries failed
#         emergency_images = _get_emergency_business_images(business_type, design_plan_text)
        
#         return {
#             'success': False,
#             'context_images': emergency_images,
#             'generation_method': 'FINAL_EMERGENCY_FALLBACK',
#             'error': str(e),
#             'image_count': len(emergency_images),
#             'business_type': business_type
#         }

# @shared_task(bind=True)
# def generate_website_with_images_task(self, plan_id, user_id):
#     """
#     Complete website generation task - NO NESTED TASKS
#     """
#     logger.info(f"Starting complete website generation for plan_id: {plan_id}")
    
#     try:
#         # Get design plan
#         design_plan = WebsiteDesignPlan.objects.get(id=plan_id, user_id=user_id)
        
#         # Extract user preferences
#         user_preferences = design_plan.design_preferences
#         business_type = _extract_business_type(design_plan.original_prompt)
        
#         # DO NOT CALL ANOTHER TASK - Generate images directly
#         logger.info("Starting direct image generation...")
        
#         # Call the function directly (not as a task)
#         image_result = generate_context_aware_images_task.run(
#             design_plan.current_plan,
#             user_preferences,
#             business_type
#         )
        
#         if not image_result['success']:
#             logger.warning(f"Image generation had issues: {image_result.get('error', 'Unknown error')}")
        
#         context_images = image_result['context_images']
#         generation_method = image_result['generation_method']
        
#         logger.info(f"Images ready: {len(context_images)} via {generation_method}")
        
#         # Generate color palette
#         primary_color = user_preferences.get('primary_color', '#4B5EAA')
#         user_theme = user_preferences.get('theme', 'light')
        
#         color_palette = ColorHarmonySystem.generate_accessible_colors(primary_color, user_theme)
#         accessibility_check = ColorHarmonySystem.validate_accessibility(color_palette)
        
#         # Generate enhanced prompt
#         enhanced_prompt = generate_enhanced_prompt(
#             design_plan=design_plan,
#             context_images=context_images,
#             user_preferences=user_preferences,
#             color_palette=color_palette,
#             accessibility_check=accessibility_check,
#             image_generation_method=generation_method
#         )
        
#         # Generate HTML with Gemini
#         logger.info("Generating HTML with Gemini...")
#         html_content = _generate_html_with_gemini(enhanced_prompt)
        
#         # Create website object
#         website = Website.objects.create(
#             user_id=user_id,
#             title=_extract_title_from_prompt(design_plan.original_prompt),
#             prompt=enhanced_prompt,
#             html_content=html_content,
#             contact_email=user_preferences.get('contact_email', ''),
#             primary_color=color_palette['primary'],
#             secondary_color=color_palette['secondary'],
#             accent_color=color_palette['accent'],
#             background_color=color_palette['background'],
#             theme=user_theme,
#             heading_font=user_preferences.get('heading_font', 'Playfair Display'),
#             body_font=user_preferences.get('body_font', 'Inter'),
#             corner_radius=user_preferences.get('corner_radius', 8)
#         )
        
#         # Mark design plan as approved
#         design_plan.is_approved = True
#         design_plan.save()
        
#         logger.info(f"Website created successfully: {website.id}")
        
#         return {
#             'success': True,
#             'website_id': website.id,
#             'context_images': context_images,
#             'color_palette': color_palette,
#             'generation_method': generation_method,
#             'accessibility_scores': accessibility_check.get('scores', {}),
#             'message': f'Website created with {generation_method} images'
#         }
        
#     except Exception as e:
#         logger.error(f"Website generation task failed: {str(e)}")
        
#         return {
#             'success': False,
#             'error': str(e),
#             'message': 'Website generation failed'
#         }

# @shared_task
# def cleanup_expired_tasks():
#     """
#     Periodic task to cleanup old Celery results
#     """
#     logger.info("Running cleanup for expired tasks...")
#     return {'status': 'cleanup_completed'}

# # Helper functions remain the same...
# def _parse_business_requirements(design_plan_text, business_type):
#     business_configs = {
#         'restaurant': {
#             'total_images': 8,
#             'sections': {
#                 'hero': {'count': 1, 'keywords': 'restaurant modern interior dining'},
#                 'about': {'count': 1, 'keywords': 'chef professional portrait'},
#                 'menu': {'count': 3, 'keywords': 'delicious food gourmet dish'},
#                 'gallery': {'count': 2, 'keywords': 'restaurant atmosphere dining'},
#                 'contact': {'count': 1, 'keywords': 'restaurant exterior location'}
#             }
#         },
#         'fitness': {
#             'total_images': 7,
#             'sections': {
#                 'hero': {'count': 1, 'keywords': 'fitness gym modern equipment'},
#                 'about': {'count': 1, 'keywords': 'fitness trainer professional'},
#                 'services': {'count': 3, 'keywords': 'gym workout fitness training'},
#                 'gallery': {'count': 2, 'keywords': 'fitness results transformation'}
#             }
#         },
#         'default': {
#             'total_images': 6,
#             'sections': {
#                 'hero': {'count': 1, 'keywords': f'{business_type} professional modern'},
#                 'about': {'count': 1, 'keywords': f'{business_type} professional portrait'},
#                 'services': {'count': 3, 'keywords': f'{business_type} service quality'},
#                 'contact': {'count': 1, 'keywords': f'{business_type} office professional'}
#             }
#         }
#     }
    
#     return business_configs.get(business_type, business_configs['default'])

# def _generate_dynamic_business_images(requirements, user_preferences):
#     simple_service = SimpleImageService()
#     images = {}
    
#     for section_name, section_data in requirements['sections'].items():
#         count = section_data['count']
#         base_keywords = section_data['keywords']
        
#         theme_modifier = user_preferences.get('theme', 'light')
#         style_modifiers = ['modern', 'professional', 'clean', 'quality']
        
#         if count == 1:
#             enhanced_keywords = f"{base_keywords} {theme_modifier} professional"
#             images[f"{section_name}_image"] = simple_service._get_unsplash_image(enhanced_keywords)
#         else:
#             for i in range(1, count + 1):
#                 modifier = style_modifiers[(i - 1) % len(style_modifiers)]
#                 enhanced_keywords = f"{base_keywords} {modifier} {theme_modifier}"
#                 images[f"{section_name}_{i}"] = simple_service._get_unsplash_image(enhanced_keywords)
    
#     logger.info(f"Generated {len(images)} dynamic business images")
#     return images

# def _get_emergency_business_images(business_type, design_plan_text):
#     emergency_configs = {
#         'restaurant': {
#             'hero_image': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200&h=600&fit=crop',
#             'about_image': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=400&fit=crop',
#             'menu_1': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=600&h=400&fit=crop',
#             'menu_2': 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=600&h=400&fit=crop',
#             'gallery_1': 'https://images.unsplash.com/photo-1559329007-40df8ac9400a?w=600&h=400&fit=crop'
#         },
#         'default': {
#             'hero_image': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200&h=600&fit=crop',
#             'about_image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop',
#             'service_1': 'https://images.unsplash.com/photo-1551434678-e076c223a692?w=600&h=400&fit=crop',
#             'service_2': 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&h=400&fit=crop',
#             'portfolio_1': 'https://images.unsplash.com/photo-1467232004584-a241de8bcf5d?w=600&h=400&fit=crop'
#         }
#     }
    
#     return emergency_configs.get(business_type, emergency_configs['default'])

# def _generate_html_with_gemini(enhanced_prompt):
#     try:
#         client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
#         contents = [
#             types.Content(
#                 role="user",
#                 parts=[types.Part.from_text(text=enhanced_prompt)],
#             ),
#         ]
        
#         response = client.models.generate_content(
#             model="gemini-2.5-flash-preview-05-20",
#             contents=contents,
#             config=types.GenerateContentConfig(response_mime_type="text/plain"),
#         )
        
#         content = response.text.strip()
        
#         if content.startswith("```html") and "```" in content[6:]:
#             content = content.replace("```html", "", 1)
#             content = content.rsplit("```", 1)[0].strip()
#         elif content.startswith("```") and content.endswith("```"):
#             content = content[3:-3].strip()
        
#         if not content.startswith("<!DOCTYPE") and not content.startswith("<html"):
#             content = f"<!DOCTYPE html>\n<html>\n<head>\n<meta charset=\"UTF-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n<title>Generated Website</title>\n</head>\n<body>\n{content}\n</body>\n</html>"
        
#         return content
        
#     except Exception as e:
#         logger.error(f"Gemini HTML generation failed: {str(e)}")
#         raise

# def _extract_business_type(prompt):
#     business_keywords = {
#         'restaurant': ['restaurant', 'cafe', 'food', 'dining', 'menu'],
#         'fitness': ['fitness', 'gym', 'workout', 'training', 'health'],
#         'photography': ['photography', 'photographer', 'photo', 'portrait', 'wedding'],
#         'tech': ['technology', 'software', 'app', 'digital', 'development'],
#         'consulting': ['consulting', 'consultant', 'advisory', 'business'],
#         'healthcare': ['health', 'medical', 'clinic', 'doctor', 'wellness'],
#         'education': ['education', 'school', 'course', 'learning', 'teaching'],
#         'retail': ['shop', 'store', 'retail', 'product', 'ecommerce']
#     }
    
#     prompt_lower = prompt.lower()
#     for business_type, keywords in business_keywords.items():
#         if any(keyword in prompt_lower for keyword in keywords):
#             return business_type
    
#     return 'general'

# def _extract_title_from_prompt(prompt):
#     words = prompt.split()
#     if len(words) <= 5:
#         return prompt
#     else:
#         return ' '.join(words[:5]) + '...'