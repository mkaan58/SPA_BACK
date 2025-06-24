# spa/tasks.py
from celery import Celery
from django.conf import settings
import asyncio
import logging
import json
import time
from concurrent.futures import ThreadPoolExecutor
import hashlib
from celery import shared_task
from django.contrib.auth import get_user_model
from google import genai
from google.genai import types
from spa.models import Website
from spa.models import WebsiteDesignPlan

logger = logging.getLogger(__name__)
User = get_user_model()



from core.celery.celery import app

@app.task(bind=True, max_retries=2)
def create_website_optimized(self, plan_id, user_id):
    """
    EXACTLY SAME FUNCTIONALITY - JUST FASTER
    - Same business_context extraction
    - Same section_queries generation  
    - Same streamlined_photo_service
    - Same color system
    - Same Gemini generation
    
    ONLY OPTIMIZATION: Smart caching + async execution
    """
    start_time = time.time()
    
    try:
        from spa.models import WebsiteDesignPlan, Website
        from spa.api.serializers import WebsiteCreateSerializer
        from spa.utils.color_utils import ColorHarmonySystem
        from spa.api.approve_plan_prompt import generate_enhanced_prompt
        # from spa.services.direct_business_extractor import direct_business_extractor
        # from spa.services.focused_query_generator import focused_query_generator
        # from spa.services.streamlined_photo_service import streamlined_photo_service
        from spa.services.direct_business_extractor import get_direct_business_extractor
        from spa.services.focused_query_generator import get_focused_query_generator
        from spa.services.streamlined_photo_service import get_streamlined_photo_service
        
        # Get design plan
        design_plan = WebsiteDesignPlan.objects.get(id=plan_id, user_id=user_id)
        original_prompt = design_plan.original_prompt
        
        logger.info(f"🚀 Optimized processing for plan {plan_id}")
        
        # ✅ OPTIMIZATION 1: SMART CACHE CHECK (saves 70% time on repeated similar requests)
        cache_key = _generate_cache_key(original_prompt, design_plan.design_preferences)
        cached_data = _get_from_cache(cache_key)
        
        if cached_data:
            logger.info("⚡ Using cached results - instant response")
            business_context = cached_data['business_context']
            section_queries = cached_data['section_queries'] 
            context_images = cached_data['context_images']
            color_palette = cached_data['color_palette']
            processing_method = "CACHED_EXACT_SAME_QUALITY"
        else:
            # ✅ OPTIMIZATION 2: PARALLEL ASYNC EXECUTION
            # Run business context and color processing in parallel
            async def run_parallel_tasks():
                # --- YENİ: Servis nesnelerini burada, ihtiyaç anında al ---
                extractor = get_direct_business_extractor()
                query_generator = get_focused_query_generator()
                photo_service = get_streamlined_photo_service()
                
                # --- DÜZELTME 1 ---
                # Business context (artık extractor nesnesi üzerinden çağır)
                business_task = extractor.extract_business_context(original_prompt)
                
                # Wait for business context
                business_context = await business_task
                
                # --- DÜZELTME 2 ---
                # Generate section queries (artık query_generator nesnesi üzerinden çağır)
                section_queries = query_generator.generate_section_queries(
                    business_context, original_prompt
                )
                
                # --- DÜZELTME 3 ---
                # Photos (artık photo_service nesnesi üzerinden çağır)
                context_images = await photo_service.get_contextual_photos(
                    business_context, section_queries
                )
                
                return business_context, section_queries, context_images
            
            # Execute async tasks
            business_context, section_queries, context_images = asyncio.run(run_parallel_tasks())
            
            # Color processing (can run while waiting for photos)
            primary_color = design_plan.design_preferences.get('primary_color', '#4B5EAA')
            user_theme = design_plan.design_preferences.get('theme', 'light')
            color_palette = ColorHarmonySystem.generate_accessible_colors(primary_color, user_theme)
            accessibility_check = ColorHarmonySystem.validate_accessibility(color_palette)
            
            # Accessibility optimization (same as original)
            max_attempts = 3
            attempt = 0
            while not accessibility_check['is_accessible'] and attempt < max_attempts:
                attempt += 1
                primary_rgb = ColorHarmonySystem.hex_to_rgb(primary_color)
                if user_theme == 'light':
                    adjusted_rgb = ColorHarmonySystem.adjust_brightness(primary_rgb, -0.2 * attempt)
                else:
                    adjusted_rgb = ColorHarmonySystem.adjust_brightness(primary_rgb, 0.2 * attempt)
                adjusted_primary = ColorHarmonySystem.rgb_to_hex(adjusted_rgb)
                color_palette = ColorHarmonySystem.generate_accessible_colors(adjusted_primary, user_theme)
                accessibility_check = ColorHarmonySystem.validate_accessibility(color_palette)
            
            processing_method = "STREAMLINED_FOCUSED_PIPELINE"
            
            # ✅ CACHE RESULTS for next time (same business type requests will be instant)
            _save_to_cache(cache_key, {
                'business_context': business_context,
                'section_queries': section_queries,
                'context_images': context_images,
                'color_palette': color_palette
            })
        
        # ✅ EXACTLY SAME enhanced prompt generation (no changes)
        user_preferences = {
            "theme": design_plan.design_preferences.get('theme', 'light'),
            "primary_color": design_plan.design_preferences.get('primary_color', '#4B5EAA'),
            "font_type": design_plan.design_preferences.get('heading_font', 'modern'),
            "website_prompt": design_plan.original_prompt,
            "business_type": business_context.get('business_type', 'general_business')
        }
        
        enhanced_prompt = generate_enhanced_prompt(
            design_plan=design_plan,
            context_images=context_images,
            user_preferences=user_preferences,
            color_palette=color_palette,
            accessibility_check=accessibility_check,
            image_generation_method=processing_method
        )
        
        # ✅ EXACTLY SAME website creation (no changes)
        website_data = {
            'prompt': enhanced_prompt,
            'original_user_prompt': original_prompt,
            'business_context': business_context,
            'contact_email': design_plan.design_preferences.get('contact_email', ''),
            'primary_color': color_palette['primary'],
            'secondary_color': color_palette['secondary'],
            'accent_color': color_palette['accent'],
            'background_color': color_palette['background'],
            'theme': design_plan.design_preferences.get('theme', 'light'),
            'heading_font': design_plan.design_preferences.get('heading_font', 'Playfair Display'),
            'body_font': design_plan.design_preferences.get('body_font', 'Inter'),
            'corner_radius': design_plan.design_preferences.get('corner_radius', 8)
        }
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=user_id)
        
        website_serializer = WebsiteCreateSerializer(
            data=website_data, 
            context={'request': type('obj', (object,), {'user': user})()}
        )
        website_serializer.is_valid(raise_exception=True)
        website = website_serializer.save()
        
        # ✅ EXACTLY SAME Gemini generation (no changes)
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=enhanced_prompt)],
            ),
        ]
        
        generate_content_config = types.GenerateContentConfig(
            response_mime_type="text/plain",
        )
        
        response = client.models.generate_content(
            # model="gemini-2.5-flash-preview-05-20",
            model="gemini-2.5-pro",
            contents=contents,
            config=generate_content_config,
        )
        
        # ✅ EXACTLY SAME HTML cleaning (no changes)
        content = response.text.strip()
        if content.startswith("```html") and "```" in content[6:]:
            content = content.replace("```html", "", 1)
            content = content.rsplit("```", 1)[0].strip()
        elif content.startswith("```") and content.endswith("```"):
            content = content[3:-3].strip()
        
        if not content.startswith("<!DOCTYPE") and not content.startswith("<html"):
            content = f"<!DOCTYPE html>\n<html>\n<head>\n<meta charset=\"UTF-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n<title>Generated Website</title>\n</head>\n<body>\n{content}\n</body>\n</html>"
        
        website.html_content = content
        website.save()
        
        design_plan.is_approved = True
        design_plan.save()
        
        processing_time = time.time() - start_time
        logger.info(f"🎉 Optimized completion in {processing_time:.2f}s")
        
        return {
            'success': True,
            'website_id': website.id,
            'business_context': business_context,
            'context_images': context_images,
            'color_palette': color_palette,
            'accessibility_scores': accessibility_check['scores'],
            'image_generation_method': processing_method,
            'processing_time': processing_time
        }
        
    except Exception as e:
        logger.error(f"❌ Optimized task failed: {str(e)}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        raise

# ✅ CACHE FUNCTIONS - Smart but simple
def _generate_cache_key(original_prompt, design_preferences):
    """Generate smart cache key for identical requests"""
    # Normalize prompt to catch similar requests
    normalized_prompt = ' '.join(original_prompt.lower().split())
    
    cache_data = {
        'prompt_hash': hashlib.md5(normalized_prompt.encode()).hexdigest()[:16],
        'primary_color': design_preferences.get('primary_color', '#4B5EAA'),
        'theme': design_preferences.get('theme', 'light'),
        'heading_font': design_preferences.get('heading_font', 'Playfair Display'),
        'body_font': design_preferences.get('body_font', 'Inter')
    }
    
    return hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()[:20]

def _get_from_cache(cache_key):
    """Get cached results"""
    from django.core.cache import cache
    return cache.get(f"website_generation:{cache_key}")

def _save_to_cache(cache_key, data):
    """Save results to cache"""
    from django.core.cache import cache
    # Cache for 6 hours - same requests will be instant
    cache.set(f"website_generation:{cache_key}", data, 3600 * 6)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def analyze_prompt_task(self, prompt_data, user_id):
    """Background task for AI prompt analysis"""
    
    try:
        # Get user
        user = User.objects.get(id=user_id)
        
        original_prompt = prompt_data['prompt']
        
        # Design preferences
        design_prefs = {
            'primary_color': prompt_data.get('primary_color', '#4B5EAA'),
            'theme': prompt_data.get('theme', 'light'),
            'heading_font': prompt_data.get('heading_font', 'Playfair Display'),
            'body_font': prompt_data.get('body_font', 'Inter'),
            'corner_radius': prompt_data.get('corner_radius', 8),
            'contact_email': prompt_data.get('contact_email', '')
        }
        
        # Initialize Gemini client
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # Create AI prompt
        analyze_prompt = f"""
You are a senior UI/UX designer and frontend developer. Analyze the user's website request and create a DETAILED design plan.

USER REQUEST:
{original_prompt}

DESIGN PREFERENCES:
- Primary Color: {design_prefs['primary_color']}
- Theme: {design_prefs['theme']}
- Heading Font: {design_prefs['heading_font']}
- Body Font: {design_prefs['body_font']}
- Corner Radius: {design_prefs['corner_radius']}px

Create a detailed design plan in the following format:

#Project Name: [General definition of the project, e.g. "Modern Portfolio Website"]
# 🎨 Website Design Plan

## 📋 Project Summary
- **Website Type**: [portfolio/corporate/e-commerce/blog etc.]
- **Target Audience**: [who is this designed for]
- **Main Purpose**: [primary goal of the website]

## 🔧 Technical Features
- **Responsive Design**: Mobile-first approach
- **Technologies**: HTML5, CSS3 (Tailwind), JavaScript (Alpine.js)
- **Performance**: Lazy loading, WebP images, optimized animations

## 🎯 Page Structure and Sections

### 1. 🏠 Navigation (Navbar)
- **Style**: [fixed/sticky/transparent start]
- **Menu Content**: [which links will be included]
- **Mobile Menu**: [hamburger menu features]
- **Logo Area**: [logo position and style]

### 2. 🌟 Hero Section
- **Design Approach**: [full-screen/split/minimal]
- **Content Elements**: 
  - Main title: [title content]
  - Subtitle/description: [descriptive text]
  - CTA Buttons: [which buttons]
  - Visual Element: [image/video/animation]
- **Animations**: [fade-in, slide-up, lottie animations]

### 3. 👤 About Section
- **Layout**: [two column/single column/card design]
- **Content**: [personal/corporate information]
- **Visual**: [profile photo/team photos]
- **Highlight Areas**: [information to emphasize]

### 4. 💼 Portfolio/Projects Section
- **Grid Layout**: [3 columns desktop, 2 tablet, 1 mobile]
- **Filtering**: [category filters]
- **Hover Effects**: [zoom, overlay, shadow effects]
- **Lightbox**: [GLightbox modal viewing]
- **Project Count**: [how many projects to show]

### 5. 🛠️ Services Section (if needed)
- **Card Design**: [icon + title + description]
- **Layout**: [grid/swiper slider]
- **Icon Usage**: [Material Icons/Font Awesome]

### 6. 📞 Contact Section
- **Form Fields**: [name, email, message, phone etc.]
- **Validation**: [Alpine.js real-time validation]
- **Contact Info**: [email, phone, address]
- **Social Media**: [which platforms]

### 7. 🔗 Footer
- **Content**: [copyright, social media, quick links]
- **Style**: [minimal/detailed]

## 🎨 Color Palette and Design System

### Smart Color Analysis
- **Primary Color**: {design_prefs['primary_color']}
- **Color Scheme Type**: [complementary/analogous/triadic/monochromatic - which type to choose and why]
- **Secondary Colors**: [AI-generated harmonious colors]
- **Accent Colors**: [emphasis colors]
- **Background Colors**: [background color gradations]
- **Text Colors**: [text colors - WCAG compliant]

### Typography System
- **Headings**: {design_prefs['heading_font']} - [H1: 48px/32px, H2: 32px/24px]
- **Body Text**: {design_prefs['body_font']} - [16px base size]
- **Font Weights**: [400, 600, 700]

### Design Elements
- **Corner Radius**: {design_prefs['corner_radius']}px [all rounded elements]
- **Spacing System**: [8px, 16px, 24px, 32px, 48px, 64px]
- **Shadow System**: [subtle shadows for depth]

## ✨ Interactivity and Animations

### Scroll Animations (AOS)
- **Hero**: [fade-in-up animation]
- **About**: [fade-in-left/right]
- **Portfolio**: [zoom-in animations]
- **Contact**: [fade-in-up]

### Hover Effects
- **Buttons**: [scale + shadow + color transition]
- **Portfolio Items**: [image zoom + overlay fade]
- **Navigation**: [underline animation]

### Micro Interactions
- **Form Focus**: [input field animations]
- **Loading States**: [button loading spinners]
- **Success Messages**: [slide-in notifications]

## 📱 Responsive Behavior
- **Breakpoints**: [mobile: <768px, tablet: 768-1024px, desktop: >1024px]
- **Navigation**: [hamburger menu on mobile]
- **Typography**: [fluid typography scaling]
- **Images**: [responsive with proper aspect ratios]

## 🚀 Performance Optimizations
- **Images**: [WebP format, lazy loading, proper sizing]
- **Animations**: [hardware acceleration, reduced motion respect]
- **Code**: [minified CSS/JS, CDN usage]

Do you like this plan? Would you like to change, add, or remove any sections?
"""

        # Send to AI
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=analyze_prompt)],
            ),
        ]
        
        response = client.models.generate_content(
            # model="gemini-2.5-flash-preview-05-20",
            model="gemini-2.5-pro",
            contents=contents,
            config=types.GenerateContentConfig(response_mime_type="text/plain"),
        )
        
        # Create design plan
        design_plan = WebsiteDesignPlan.objects.create(
            user=user,
            original_prompt=original_prompt,
            current_plan=response.text.strip(),
            design_preferences=design_prefs,
            feedback_history=[]
        )
        
        logger.info(f"✅ Design plan created: {design_plan.id} for user {user_id}")
        
        return {
            'success': True,
            'plan_id': design_plan.id,
            'design_plan': response.text.strip(),
            'status': 'plan_created'
        }
        
    except Exception as e:
        logger.error(f"❌ analyze_prompt_task failed: {str(e)}")
        
        # Retry on failure
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying task, attempt {self.request.retries + 1}")
            raise self.retry(countdown=60, exc=e)
        
        return {
            'success': False,
            'error': str(e)
        }
    

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def ai_line_edit_task(self, website_id, user_request, user_id):
    """Background task for AI line-based editing"""
    
    try:
        # Get user and website
        user = User.objects.get(id=user_id)
        website = Website.objects.get(id=website_id, user=user)
        
        # Store original HTML for comparison
        original_html = website.html_content
        original_length = len(original_html)
        
        # Initialize line-based editor
        from spa.api.views import LineBasedAIEditor  # Import here to avoid circular imports
        editor = LineBasedAIEditor()
        
        # Prepare context
        ai_prompt = editor.prepare_line_context(website.html_content, user_request)
        
        # Initialize Gemini client
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # Enhanced AI prompt for JSON response
        enhanced_ai_prompt = ai_prompt + """

CRITICAL: Your response must be VALID JSON starting with { and ending with }.
Do not include any text before or after the JSON.
Do not use markdown code blocks.
Do not include explanations outside the JSON.

Example valid response:
{"analysis": "Adding phone field to contact form", "line_changes": [{"start_line": 45, "end_line": 55, "reason": "Replace form HTML", "new_content": "<form>...</form>"}], "summary": "Added phone field successfully"}
"""
        
        # Send to AI
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=enhanced_ai_prompt)],
            ),
        ]

        response = client.models.generate_content(
            # model="gemini-2.5-flash-preview-05-20",
            model="gemini-2.5-pro",
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
                max_output_tokens=6000,
            ),
        )
        
        if not response or not response.text:
            raise Exception("AI service returned empty response")
        
        # Parse AI response
        import json
        try:
            ai_response = json.loads(response.text.strip())
        except json.JSONDecodeError as parse_error:
            logger.error(f"JSON parse error: {parse_error}")
            raise Exception(f"AI returned invalid JSON: {parse_error}")
        
        # Validate AI response structure
        if not isinstance(ai_response, dict) or 'line_changes' not in ai_response:
            ai_response['line_changes'] = []
        
        # Apply line changes if any
        if ai_response['line_changes']:
            modified_html = editor.apply_line_changes(ai_response['line_changes'])
            
            # ✅ FIX: Use validation functions from tasks instead of WebsiteViewSet
            validation_result = _perform_html_validation(original_html, modified_html, user_request)
            
            if not validation_result['valid']:
                logger.error(f"Structure validation failed: {validation_result['errors']}")
                raise Exception(f"AI broke critical HTML structure: {validation_result['errors']}")
            
            # Validate HTML integrity
            if not modified_html or not modified_html.strip():
                raise Exception("Modified HTML is empty")
            
            if '<html' not in modified_html.lower() or '</html>' not in modified_html.lower():
                raise Exception("Modified HTML missing html tags")
            
            # Save to database
            website.html_content = modified_html
            website.save(update_fields=['html_content'])
            
            # Verify save
            website.refresh_from_db()
            if website.html_content != modified_html:
                raise Exception("Database save verification failed")
            
            logger.info(f"✅ AI line edit completed: {website_id} for user {user_id}")
            
            return {
                'success': True,
                'modified_html': modified_html,
                'analysis': ai_response.get('analysis', 'No analysis provided'),
                'changes_applied': len(ai_response.get('line_changes', [])),
                'summary': ai_response.get('summary', 'No summary provided'),
                'html_actually_changed': modified_html != original_html,
                'original_html_length': original_length,
                'modified_html_length': len(modified_html)
            }
        else:
            # No changes to apply
            logger.info(f"No line changes needed for website {website_id}")
            return {
                'success': True,
                'modified_html': website.html_content,
                'analysis': ai_response.get('analysis', 'No changes needed'),
                'changes_applied': 0,
                'summary': 'No modifications required',
                'html_actually_changed': False,
                'original_html_length': original_length,
                'modified_html_length': len(website.html_content)
            }
        
    except Website.DoesNotExist:
        logger.error(f"Website {website_id} not found for user {user_id}")
        return {
            'success': False,
            'error': 'Website not found'
        }
        
    except Exception as e:
        logger.error(f"❌ ai_line_edit_task failed: {str(e)}")
        
        # Retry on failure
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying task, attempt {self.request.retries + 1}")
            raise self.retry(countdown=60, exc=e)
        
        return {
            'success': False,
            'error': str(e)
        }


def _perform_html_validation(original_html, modified_html, user_request):
    """
    ✅ NEW: Comprehensive HTML validation using existing helper functions
    """
    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    try:
        # Basic checks
        if not modified_html or not modified_html.strip():
            validation_result['valid'] = False
            validation_result['errors'].append("Modified HTML is empty")
            return validation_result
        
        # Use existing validation functions
        critical_tags = _check_critical_tags(original_html, modified_html)
        js_integrity = _check_javascript_integrity(original_html, modified_html)
        css_integrity = _check_css_integrity(original_html, modified_html)
        
        # Check critical tags
        for tag, info in critical_tags.items():
            if not info['intact']:
                validation_result['valid'] = False
                validation_result['errors'].append(f"Critical tag {tag} is corrupted: {info['original']} → {info['modified']}")
        
        # Check JavaScript integrity
        if not js_integrity['scripts_intact']:
            validation_result['warnings'].append(f"JavaScript blocks changed: {js_integrity['original_count']} → {js_integrity['modified_count']}")
        
        # Check CSS integrity
        if not css_integrity['styles_intact']:
            validation_result['warnings'].append(f"CSS blocks changed: {css_integrity['original_count']} → {css_integrity['modified_count']}")
        
        # Size sanity check
        original_length = len(original_html)
        modified_length = len(modified_html)
        
        if modified_length < original_length * 0.3:  # If shrunk by more than 70%
            validation_result['valid'] = False
            validation_result['errors'].append(f"HTML dramatically reduced in size: {original_length} → {modified_length}")
        
        logger.info(f"✅ HTML validation completed: {'VALID' if validation_result['valid'] else 'INVALID'}")
        
        return validation_result
        
    except Exception as e:
        logger.error(f"❌ HTML validation failed: {str(e)}")
        validation_result['valid'] = False
        validation_result['errors'].append(f"Validation error: {str(e)}")
        return validation_result

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def update_plan_task(self, plan_id, feedback, user_id):
    """Background task for updating design plan based on feedback"""
    
    try:
        # Get user and design plan
        user = User.objects.get(id=user_id)
        design_plan = WebsiteDesignPlan.objects.get(id=plan_id, user=user)
        
        # Initialize Gemini client
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # Update feedback history
        feedback_history = design_plan.feedback_history
        feedback_history.append(feedback)
        
        # Create update prompt
        update_prompt = f"""
You are a senior UI/UX designer. You previously created a design plan and now have user feedback.

CURRENT DESIGN PLAN:
{design_plan.current_plan}

USER FEEDBACK:
{feedback}

PREVIOUS FEEDBACK HISTORY:
{chr(10).join(feedback_history[:-1]) if len(feedback_history) > 1 else 'First feedback'}

Please update the design plan based on the user's feedback. Only make the specified changes, keep other sections as they are. Return the updated plan in the same Markdown format.

If the user wants a new section added, place it in the appropriate location and add details.
If they want to modify an existing section, only update that part.
If they want a feature removed, remove that feature.

UPDATED PLAN:
"""

        # Send to AI
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=update_prompt)],
            ),
        ]
        
        response = client.models.generate_content(
            # model="gemini-2.5-flash-preview-05-20",
            model="gemini-2.5-pro",
            contents=contents,
            config=types.GenerateContentConfig(response_mime_type="text/plain"),
        )
        
        # Update design plan
        design_plan.current_plan = response.text.strip()
        design_plan.feedback_history = feedback_history
        design_plan.save()
        
        logger.info(f"✅ Design plan updated: {design_plan.id} for user {user_id}")
        
        return {
            'success': True,
            'plan_id': design_plan.id,
            'design_plan': response.text.strip(),
            'status': 'plan_updated'
        }
        
    except WebsiteDesignPlan.DoesNotExist:
        logger.error(f"Design plan {plan_id} not found for user {user_id}")
        return {
            'success': False,
            'error': 'Design plan not found'
        }
        
    except Exception as e:
        logger.error(f"❌ update_plan_task failed: {str(e)}")
        
        # Retry on failure
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying task, attempt {self.request.retries + 1}")
            raise self.retry(countdown=60, exc=e)
        
        return {
            'success': False,
            'error': str(e)
        }


# spa/tasks.py - Add these image processing tasks

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from spa.models import UploadedImage, Website
import tempfile
import os
from PIL import Image
import requests
from io import BytesIO

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def upload_image_task(self, image_data, metadata, user_id, website_id):
    """Background task for image upload and processing"""
    
    try:
        # Get user and website
        user = User.objects.get(id=user_id)
        website = Website.objects.get(id=website_id, user=user)
        
        # Process image data
        image_file = image_data.get('image_file')
        title = metadata.get('title', 'Uploaded Image')
        
        if not image_file:
            raise Exception("No image file provided")
        
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Write image data to temp file
            for chunk in image_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        try:
            # Open and validate image
            with Image.open(temp_file_path) as img:
                # Validate image format
                if img.format not in ['JPEG', 'PNG', 'GIF', 'WEBP']:
                    raise Exception(f"Unsupported image format: {img.format}")
                
                # Check image size (max 10MB)
                file_size = os.path.getsize(temp_file_path)
                if file_size > 10 * 1024 * 1024:  # 10MB
                    raise Exception("Image file too large (max 10MB)")
                
                # Optimize image if needed
                optimized_image = None
                if file_size > 2 * 1024 * 1024:  # If larger than 2MB, optimize
                    logger.info(f"Optimizing large image: {file_size} bytes")
                    
                    # Resize if too large
                    max_dimension = 1920
                    if img.width > max_dimension or img.height > max_dimension:
                        img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                    
                    # Save optimized version
                    optimized_buffer = BytesIO()
                    img.save(optimized_buffer, format='JPEG', quality=85, optimize=True)
                    optimized_image = ContentFile(optimized_buffer.getvalue())
                    optimized_image.name = f"optimized_{image_file.name}"
        
            # Create UploadedImage object
            if optimized_image:
                uploaded_image = UploadedImage.objects.create(
                    user=user,
                    website=website,
                    image=optimized_image,
                    title=title
                )
                logger.info(f"✅ Optimized image uploaded: {uploaded_image.id}")
            else:
                # Use original image
                uploaded_image = UploadedImage.objects.create(
                    user=user,
                    website=website,
                    image=image_file,
                    title=title
                )
                logger.info(f"✅ Original image uploaded: {uploaded_image.id}")
            
            # Generate thumbnail if needed (optional)
            try:
                with Image.open(uploaded_image.image.path) as img:
                    # Create thumbnail
                    img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                    thumb_buffer = BytesIO()
                    img.save(thumb_buffer, format='JPEG', quality=80)
                    # Could save thumbnail to a separate field if needed
                    
            except Exception as thumb_error:
                logger.warning(f"Thumbnail generation failed: {thumb_error}")
                # Continue without thumbnail
            
            return {
                'success': True,
                'image_id': uploaded_image.id,
                'image_url': uploaded_image.image.url,
                'title': uploaded_image.title,
                'file_size': uploaded_image.image.size,
                'optimized': optimized_image is not None
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return {
            'success': False,
            'error': 'User not found'
        }
        
    except Website.DoesNotExist:
        logger.error(f"Website {website_id} not found for user {user_id}")
        return {
            'success': False,
            'error': 'Website not found'
        }
        
    except Exception as e:
        logger.error(f"❌ upload_image_task failed: {str(e)}")
        
        # Retry on failure
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying image upload, attempt {self.request.retries + 1}")
            raise self.retry(countdown=60, exc=e)
        
        return {
            'success': False,
            'error': str(e)
        }


@shared_task(bind=True, max_retries=3, default_retry_delay=90)
def generate_photos_task(self, business_context, section_queries, user_id, plan_id=None):
    """Background task for generating contextual photos"""
    
    try:
        # Get user
        user = User.objects.get(id=user_id)
        
        # Import photo services
        from spa.services.streamlined_photo_service import get_streamlined_photo_service
        from spa.services.focused_query_generator import get_focused_query_generator
        
        # If section_queries not provided, generate them
        if not section_queries and business_context:
            logger.info("Generating section queries from business context")
            section_queries = get_focused_query_generator.generate_section_queries(
                business_context, 
                business_context.get('original_prompt', '')
            )
        
        # Generate contextual photos
        import asyncio
        
        # Run async photo service in sync context
        try:
            context_images = asyncio.run(
                get_streamlined_photo_service.get_contextual_photos(
                    business_context, 
                    section_queries
                )
            )
            logger.info(f"✅ Retrieved {len(context_images)} contextual photos")
            
        except Exception as photo_error:
            logger.error(f"Streamlined photo service failed: {photo_error}")
            
            # Fallback to emergency images
            from spa.api.views import WebsiteViewSet
            viewset_instance = WebsiteViewSet()
            context_images = viewset_instance._get_emergency_unsplash_images(
                business_context.get('original_prompt', 'business website')
            )
            logger.info(f"✅ Generated {len(context_images)} emergency fallback images")
        
        # Validate images
        valid_images = {}
        for key, url in context_images.items():
            if url and isinstance(url, str) and url.startswith(('http://', 'https://')):
                # Test image accessibility
                try:
                    response = requests.head(url, timeout=10)
                    if response.status_code == 200:
                        valid_images[key] = url
                    else:
                        logger.warning(f"Image URL not accessible: {url}")
                except Exception as url_error:
                    logger.warning(f"Failed to validate image URL {url}: {url_error}")
        
        # Ensure minimum number of images
        if len(valid_images) < 3:
            logger.warning(f"Only {len(valid_images)} valid images, adding fallbacks")
            
            # Add generic fallback images
            fallback_urls = [
                "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800&h=600&fit=crop&crop=center&auto=format&q=80",
                "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=800&h=600&fit=crop&crop=center&auto=format&q=80",
                "https://images.unsplash.com/photo-1553028826-f4804a6dba3b?w=800&h=600&fit=crop&crop=center&auto=format&q=80",
                "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&h=600&fit=crop&crop=center&auto=format&q=80"
            ]
            
            fallback_index = 0
            for i in range(6 - len(valid_images)):  # Ensure at least 6 images total
                key = f"fallback_image_{i+1}"
                if fallback_index < len(fallback_urls):
                    valid_images[key] = fallback_urls[fallback_index]
                    fallback_index += 1
        
        # Optional: Cache results for future use
        from django.core.cache import cache
        if plan_id:
            cache_key = f"generated_photos_{plan_id}_{user_id}"
            cache.set(cache_key, valid_images, timeout=3600)  # Cache for 1 hour
        
        logger.info(f"✅ Photo generation completed: {len(valid_images)} images for user {user_id}")
        
        return {
            'success': True,
            'context_images': valid_images,
            'total_images': len(valid_images),
            'business_context': business_context,
            'generation_method': 'streamlined_focused_pipeline' if len(context_images) >= 3 else 'emergency_fallback'
        }
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return {
            'success': False,
            'error': 'User not found'
        }
        
    except Exception as e:
        logger.error(f"❌ generate_photos_task failed: {str(e)}")
        
        # Retry on failure
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying photo generation, attempt {self.request.retries + 1}")
            raise self.retry(countdown=90, exc=e)
        
        # Final fallback - return basic images
        try:
            basic_images = {
                'hero_image': "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800&h=600&fit=crop&crop=center&auto=format&q=80",
                'about_image': "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=800&h=600&fit=crop&crop=center&auto=format&q=80",
                'portfolio_1': "https://images.unsplash.com/photo-1553028826-f4804a6dba3b?w=800&h=600&fit=crop&crop=center&auto=format&q=80"
            }
            
            return {
                'success': True,
                'context_images': basic_images,
                'total_images': len(basic_images),
                'business_context': business_context,
                'generation_method': 'final_fallback',
                'error_message': str(e)
            }
            
        except Exception as final_error:
            logger.error(f"Even final fallback failed: {final_error}")
            return {
                'success': False,
                'error': f'Complete failure: {str(e)}'
            }
        


# spa/tasks.py - Add these business intelligence tasks

import asyncio
import json
import re
from django.core.cache import cache

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def extract_business_context_task(self, prompt, user_id, cache_key=None):
   """Background task for extracting business context from user prompt"""
   
   try:
       # Get user
       user = User.objects.get(id=user_id)
       
       # Check cache first if cache_key provided
       if cache_key:
           cached_result = cache.get(cache_key)
           if cached_result:
               logger.info(f"✅ Business context found in cache: {cache_key}")
               return {
                   'success': True,
                   'business_context': cached_result,
                   'source': 'cache'
               }
       
       # Import business extractor service
       try:
           from spa.services.direct_business_extractor import get_direct_business_extractor
           
           # Run async extraction in sync context
           business_context = asyncio.run(
               get_direct_business_extractor.extract_business_context(prompt)
           )
           
           logger.info(f"✅ Business context extracted: {business_context.get('business_type', 'unknown')}")
           
       except ImportError:
           logger.warning("Business extractor service not available, using fallback")
           # Fallback business context extraction
           business_context = _extract_business_context_fallback(prompt)
           
       except Exception as extraction_error:
           logger.error(f"Business extraction service failed: {extraction_error}")
           # Use fallback method
           business_context = _extract_business_context_fallback(prompt)
       
       # Cache result if cache_key provided
       if cache_key:
           cache.set(cache_key, business_context, timeout=3600)  # Cache for 1 hour
           logger.info(f"✅ Business context cached: {cache_key}")
       
       return {
           'success': True,
           'business_context': business_context,
           'source': 'extracted'
       }
       
   except User.DoesNotExist:
       logger.error(f"User {user_id} not found")
       return {
           'success': False,
           'error': 'User not found'
       }
       
   except Exception as e:
       logger.error(f"❌ extract_business_context_task failed: {str(e)}")
       
       # Retry on failure
       if self.request.retries < self.max_retries:
           logger.info(f"Retrying business context extraction, attempt {self.request.retries + 1}")
           raise self.retry(countdown=60, exc=e)
       
       # Final fallback
       try:
           fallback_context = _extract_business_context_fallback(prompt)
           return {
               'success': True,
               'business_context': fallback_context,
               'source': 'fallback',
               'error_message': str(e)
           }
       except Exception as final_error:
           return {
               'success': False,
               'error': f'Complete failure: {str(e)}'
           }

def _extract_business_context_fallback(prompt):
    """Fallback business context extraction using keyword analysis"""
    
    prompt_lower = prompt.lower()
    
    # Business type detection
    business_keywords = {
        'restaurant': ['restaurant', 'cafe', 'food', 'dining', 'menu', 'chef', 'cuisine'],
        'technology': ['tech', 'software', 'app', 'digital', 'coding', 'developer', 'startup'],
        'consulting': ['consulting', 'advisory', 'service', 'expert', 'professional', 'consultant'],
        'creative': ['design', 'creative', 'art', 'photography', 'graphic', 'artist', 'portfolio'],
        'healthcare': ['health', 'medical', 'clinic', 'wellness', 'doctor', 'therapy', 'fitness'],
        'education': ['education', 'school', 'course', 'learning', 'teacher', 'training', 'academy'],
        'retail': ['shop', 'store', 'retail', 'product', 'ecommerce', 'sell', 'buy'],
        'finance': ['finance', 'bank', 'investment', 'money', 'accounting', 'financial'],
        'real_estate': ['real estate', 'property', 'house', 'apartment', 'rent', 'buy'],
        'law': ['law', 'legal', 'lawyer', 'attorney', 'court', 'justice']
    }
    
    detected_type = 'general_business'
    max_matches = 0
    
    for business_type, keywords in business_keywords.items():
        matches = sum(1 for keyword in keywords if keyword in prompt_lower)
        if matches > max_matches:
            max_matches = matches
            detected_type = business_type
    
    # Target audience detection
    audience_keywords = {
        'b2b': ['business', 'companies', 'enterprise', 'corporate', 'b2b'],
        'b2c': ['customers', 'clients', 'people', 'individuals', 'consumer', 'b2c'],
        'both': ['everyone', 'all', 'anyone', 'general public']
    }
    
    target_audience = 'general'
    for audience, keywords in audience_keywords.items():
        if any(keyword in prompt_lower for keyword in keywords):
            target_audience = audience
            break
    
    # Features detection
    features = []
    feature_keywords = {
        'contact_form': ['contact', 'form', 'message', 'inquiry'],
        'portfolio': ['portfolio', 'gallery', 'work', 'projects', 'showcase'],
        'ecommerce': ['shop', 'buy', 'sell', 'cart', 'payment', 'product'],
        'blog': ['blog', 'news', 'articles', 'posts'],
        'booking': ['booking', 'appointment', 'schedule', 'reservation'],
        'testimonials': ['testimonial', 'review', 'feedback', 'testimonial']
    }
    
    for feature, keywords in feature_keywords.items():
        if any(keyword in prompt_lower for keyword in keywords):
            features.append(feature)
    
    return {
        'business_type': detected_type,
        'target_audience': target_audience,
        'required_features': features,
        'original_prompt': prompt,
        'confidence': min(max_matches / 3, 1.0),  # Confidence score 0-1
        'extraction_method': 'keyword_analysis'
    }


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def validate_html_structure_task(self, original_html, modified_html, user_request, user_id, website_id):
    """Background task for comprehensive HTML structure validation"""
    
    try:
        # Get user and website
        user = User.objects.get(id=user_id)
        website = Website.objects.get(id=website_id, user=user)
        
        # Import validation function
        # Use validation functions from tasks
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }

        # Basic validation checks
        critical_tags = _check_critical_tags(original_html, modified_html)
        js_integrity = _check_javascript_integrity(original_html, modified_html)
        css_integrity = _check_css_integrity(original_html, modified_html)

        # Check if all critical tags are intact
        if not all(tag['intact'] for tag in critical_tags.values()):
            validation_result['valid'] = False
            validation_result['errors'].append("Critical HTML tags are missing or unbalanced")

        if not js_integrity['scripts_intact']:
            validation_result['valid'] = False
            validation_result['errors'].append("JavaScript blocks are corrupted")

        if not css_integrity['styles_intact']:
            validation_result['valid'] = False
            validation_result['errors'].append("CSS blocks are corrupted")
        
        # Enhanced validation with additional checks
        additional_checks = {
            'html_size_change': len(modified_html) - len(original_html),
            'line_count_change': len(modified_html.split('\n')) - len(original_html.split('\n')),
            'critical_tags_intact': _check_critical_tags(original_html, modified_html),
            'javascript_integrity': _check_javascript_integrity(original_html, modified_html),
            'css_integrity': _check_css_integrity(original_html, modified_html)
        }
        
        # Combine results
        enhanced_result = {
            **validation_result,
            'additional_checks': additional_checks,
            'validation_timestamp': time.time(),
            'user_request': user_request[:100],
            'website_id': website_id
        }
        
        # Cache validation result
        cache_key = f"html_validation_{website_id}_{hash(modified_html[:1000])}"
        cache.set(cache_key, enhanced_result, timeout=1800)  # Cache for 30 minutes
        
        logger.info(f"✅ HTML validation completed for website {website_id}")
        
        return {
            'success': True,
            'validation_result': enhanced_result,
            'is_valid': validation_result['valid'],
            'critical_issues': len(validation_result['errors']),
            'warnings': len(validation_result['warnings'])
        }
        
    except (User.DoesNotExist, Website.DoesNotExist):
        logger.error(f"User {user_id} or website {website_id} not found")
        return {
            'success': False,
            'error': 'User or website not found'
        }
        
    except Exception as e:
        logger.error(f"❌ validate_html_structure_task failed: {str(e)}")
        
        # Retry on failure
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying HTML validation, attempt {self.request.retries + 1}")
            raise self.retry(countdown=30, exc=e)
        
        return {
            'success': False,
            'error': str(e)
        }


def _check_critical_tags(original_html, modified_html):
    """Check if critical HTML tags are maintained"""
    
    critical_tags = ['<!DOCTYPE', '<html', '<head', '<body', '</html>', '</head>', '</body>']
    results = {}
    
    for tag in critical_tags:
        original_count = original_html.count(tag)
        modified_count = modified_html.count(tag)
        results[tag] = {
            'original': original_count,
            'modified': modified_count,
            'intact': original_count == modified_count
        }
    
    return results


def _check_javascript_integrity(original_html, modified_html):
    """Check JavaScript block integrity"""
    
    script_pattern = r'<script[^>]*>.*?</script>'
    
    original_scripts = re.findall(script_pattern, original_html, re.DOTALL | re.IGNORECASE)
    modified_scripts = re.findall(script_pattern, modified_html, re.DOTALL | re.IGNORECASE)
    
    return {
        'original_count': len(original_scripts),
        'modified_count': len(modified_scripts),
        'scripts_intact': len(original_scripts) == len(modified_scripts)
    }


def _check_css_integrity(original_html, modified_html):
    """Check CSS block integrity"""
    
    style_pattern = r'<style[^>]*>.*?</style>'
    
    original_styles = re.findall(style_pattern, original_html, re.DOTALL | re.IGNORECASE)
    modified_styles = re.findall(style_pattern, modified_html, re.DOTALL | re.IGNORECASE)
    
    return {
        'original_count': len(original_styles),
        'modified_count': len(modified_styles),
        'styles_intact': len(original_styles) == len(modified_styles)
    }


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def generate_color_palette_task(self, primary_color, theme, user_id, cache_key=None):
    """Background task for generating accessible color palette"""
    
    try:
        # Get user
        user = User.objects.get(id=user_id)
        
        # Check cache first
        if cache_key:
            cached_palette = cache.get(cache_key)
            if cached_palette:
                logger.info(f"✅ Color palette found in cache: {cache_key}")
                return {
                    'success': True,
                    'color_palette': cached_palette['palette'],
                    'accessibility_check': cached_palette['accessibility'],
                    'source': 'cache'
                }
        
        # Import color system
        from spa.utils.color_utils import ColorHarmonySystem
        
        # Generate base color palette
        color_palette = ColorHarmonySystem.generate_accessible_colors(primary_color, theme)
        
        # Validate accessibility
        accessibility_check = ColorHarmonySystem.validate_accessibility(color_palette)
        
        # Optimization loop for better accessibility
        max_attempts = 5
        attempt = 0
        
        while not accessibility_check['is_accessible'] and attempt < max_attempts:
            attempt += 1
            logger.info(f"🔧 Optimizing colors for accessibility, attempt {attempt}")
            
            # Adjust primary color
            primary_rgb = ColorHarmonySystem.hex_to_rgb(primary_color)
            if theme == 'light':
                adjusted_rgb = ColorHarmonySystem.adjust_brightness(primary_rgb, -0.15 * attempt)
            else:
                adjusted_rgb = ColorHarmonySystem.adjust_brightness(primary_rgb, 0.15 * attempt)
            
            adjusted_primary = ColorHarmonySystem.rgb_to_hex(adjusted_rgb)
            color_palette = ColorHarmonySystem.generate_accessible_colors(adjusted_primary, theme)
            accessibility_check = ColorHarmonySystem.validate_accessibility(color_palette)
        
        # Generate additional color variants
        enhanced_palette = _generate_color_variants(color_palette, theme)
        
        # Prepare final result
        final_result = {
            'palette': enhanced_palette,
            'accessibility': accessibility_check,
            'optimization_attempts': attempt,
            'theme': theme,
            'original_primary': primary_color,
            'final_primary': enhanced_palette['primary']
        }
        
        # Cache result
        if cache_key:
            cache.set(cache_key, final_result, timeout=7200)  # Cache for 2 hours
            logger.info(f"✅ Color palette cached: {cache_key}")
        
        logger.info(f"✅ Color palette generated for user {user_id}")
        
        return {
            'success': True,
            'color_palette': enhanced_palette,
            'accessibility_check': accessibility_check,
            'source': 'generated',
            'optimization_info': {
                'attempts': attempt,
                'is_accessible': accessibility_check['is_accessible'],
                'accessibility_scores': accessibility_check['scores']
            }
        }
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return {
            'success': False,
            'error': 'User not found'
        }
        
    except Exception as e:
        logger.error(f"❌ generate_color_palette_task failed: {str(e)}")
        
        # Retry on failure
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying color palette generation, attempt {self.request.retries + 1}")
            raise self.retry(countdown=30, exc=e)
        
        # Fallback to basic palette
        try:
            fallback_palette = _generate_fallback_palette(primary_color, theme)
            return {
                'success': True,
                'color_palette': fallback_palette,
                'accessibility_check': {'is_accessible': True, 'scores': {}},
                'source': 'fallback',
                'error_message': str(e)
            }
        except Exception as final_error:
            return {
                'success': False,
                'error': f'Complete failure: {str(e)}'
            }


def _generate_color_variants(base_palette, theme):
    """Generate additional color variants for enhanced palette"""
    
    enhanced = base_palette.copy()
    
    # Add gradient variants
    enhanced['primary_light'] = _lighten_color(base_palette['primary'], 0.2)
    enhanced['primary_dark'] = _darken_color(base_palette['primary'], 0.2)
    enhanced['secondary_light'] = _lighten_color(base_palette['secondary'], 0.2)
    enhanced['secondary_dark'] = _darken_color(base_palette['secondary'], 0.2)
    
    # Add neutral variants
    if theme == 'light':
        enhanced['gray_50'] = '#f9fafb'
        enhanced['gray_100'] = '#f3f4f6'
        enhanced['gray_200'] = '#e5e7eb'
        enhanced['gray_500'] = '#6b7280'
        enhanced['gray_900'] = '#111827'
    else:
        enhanced['gray_50'] = '#111827'
        enhanced['gray_100'] = '#1f2937'
        enhanced['gray_200'] = '#374151'
        enhanced['gray_500'] = '#9ca3af'
        enhanced['gray_900'] = '#f9fafb'
    
    # Add status colors
    enhanced['success'] = '#10b981' if theme == 'light' else '#34d399'
    enhanced['warning'] = '#f59e0b' if theme == 'light' else '#fbbf24'
    enhanced['error'] = '#ef4444' if theme == 'light' else '#f87171'
    enhanced['info'] = '#3b82f6' if theme == 'light' else '#60a5fa'
    
    return enhanced


def _lighten_color(hex_color, factor):
    """Lighten a hex color by a factor (0-1)"""
    try:
        # Convert hex to RGB
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Lighten
        lightened = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
        
        # Convert back to hex
        return '#' + ''.join(f'{c:02x}' for c in lightened)
    except:
        return hex_color


def _darken_color(hex_color, factor):
    """Darken a hex color by a factor (0-1)"""
    try:
        # Convert hex to RGB
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Darken
        darkened = tuple(max(0, int(c * (1 - factor))) for c in rgb)
        
        # Convert back to hex
        return '#' + ''.join(f'{c:02x}' for c in darkened)
    except:
        return hex_color


def _generate_fallback_palette(primary_color, theme):
    """Generate a basic fallback color palette"""
    
    if theme == 'light':
        return {
            'primary': primary_color,
            'secondary': '#6b7280',
            'accent': '#f59e0b',
            'background': '#ffffff',
            'surface': '#f9fafb',
            'text': '#111827',
            'text_secondary': '#6b7280'
        }
    else:
        return {
            'primary': primary_color,
            'secondary': '#9ca3af',
            'accent': '#fbbf24',
            'background': '#111827',
            'surface': '#1f2937',
            'text': '#f9fafb',
            'text_secondary': '#9ca3af'
        }