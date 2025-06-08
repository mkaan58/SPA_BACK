#core/spa/api/views.py
import os
import logging
import re
from google import genai
from openai import OpenAI
from google.genai import types
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from spa.api.approve_plan_prompt import generate_enhanced_prompt
from spa.models import Website, UploadedImage, WebsiteDesignPlan
from .serializers import (
    WebsiteSerializer, 
    WebsiteCreateSerializer, 
    UploadedImageSerializer,
    WebsiteDesignPlanSerializer,
    AnalyzePromptSerializer,
    UpdatePlanSerializer
)
from rest_framework.parsers import MultiPartParser, FormParser
from .template_prompts.base_html_2 import BASE_HTML_TEMPLATE
import time

from playwright.async_api import async_playwright
import tempfile
import os
from django.core.files.base import ContentFile
import asyncio
from asgiref.sync import sync_to_async
from concurrent.futures import ThreadPoolExecutor
import threading

from .pagination import StandardResultsSetPagination  # Import pagination

import asyncio
import json

# Mevcut import'ların altına ekle
from spa.services.direct_business_extractor import direct_business_extractor
from spa.services.focused_query_generator import focused_query_generator
from spa.services.streamlined_photo_service import streamlined_photo_service

from asgiref.sync import sync_to_async
from typing import Dict, List


logger = logging.getLogger(__name__)

# Base HTML Template - Modern Website with all features


class WebsiteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination  # Pagination ekleyin    

    def get_queryset(self):
        return Website.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        return WebsiteSerializer
    
    def list(self, request, *args, **kwargs):
        """
        Override list method to ensure pagination is applied
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

    def _validate_fastmcp_images(self, images: Dict) -> bool:
        """FastMCP images doğrula"""
        if not images or not isinstance(images, dict):
            return False
        
        valid_urls = 0
        for key, url in images.items():
            if url and isinstance(url, str) and url.startswith('https://'):
                if 'unsplash.com' in url or 'images.unsplash.com' in url:
                    valid_urls += 1
        
        return valid_urls >= 3


    @action(detail=False, methods=['post'])
    def analyze_prompt(self, request):
        """Analyze user prompt and create detailed design plan"""
        serializer = AnalyzePromptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        original_prompt = serializer.validated_data['prompt']  # YENİ: Original prompt'u sakla
        
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            design_prefs = {
                'primary_color': serializer.validated_data.get('primary_color', '#4B5EAA'),
                'theme': serializer.validated_data.get('theme', 'light'),
                'heading_font': serializer.validated_data.get('heading_font', 'Playfair Display'),
                'body_font': serializer.validated_data.get('body_font', 'Inter'),
                'corner_radius': serializer.validated_data.get('corner_radius', 8),
                'contact_email': serializer.validated_data.get('contact_email', '')  # YENİ ALAN
            }
            
            # YENİ: Business context extraction
            try:
                business_context = asyncio.run(
                    direct_business_extractor.extract_business_context(original_prompt)
                )
                logger.info(f"✅ Business context extracted: {business_context.get('business_type', 'unknown')}")
            except Exception as e:
                logger.error(f"❌ Business context extraction failed: {e}")
                business_context = {}
            
            analyze_prompt = f"""
    You are a senior UI/UX designer and frontend developer. Analyze the user's website request and create a DETAILED design plan.

    USER REQUEST:
    {original_prompt}

    BUSINESS CONTEXT DETECTED:
    {json.dumps(business_context, indent=2) if business_context else 'No specific business context detected'}

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

            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=analyze_prompt)],
                ),
            ]
            
            generate_content_config = types.GenerateContentConfig(
                response_mime_type="text/plain",
            )
            
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                contents=contents,
                config=generate_content_config,
            )
            
            design_plan = WebsiteDesignPlan.objects.create(
                user=request.user,
                original_prompt=original_prompt,  # YENİ: Original prompt sakla
                current_plan=response.text.strip(),
                design_preferences=design_prefs,
                feedback_history=[]
            )
            
            return Response({
                'plan_id': design_plan.id,
                'design_plan': response.text.strip(),
                'business_context': business_context,  # YENİ: Business context döndür
                'status': 'plan_created'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.exception(f"Error analyzing prompt: {str(e)}")
            return Response({
                'error': f"Failed to analyze prompt: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='update-plan/(?P<plan_id>[^/.]+)')
    def update_plan(self, request, plan_id=None):
        """Update design plan based on user feedback"""
        try:
            design_plan = WebsiteDesignPlan.objects.get(id=plan_id, user=request.user)
        except WebsiteDesignPlan.DoesNotExist:
            return Response({'error': 'Design plan not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UpdatePlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            feedback_history = design_plan.feedback_history
            feedback_history.append(serializer.validated_data['feedback'])
            
            update_prompt = f"""
You are a senior UI/UX designer. You previously created a design plan and now have user feedback.

CURRENT DESIGN PLAN:
{design_plan.current_plan}

USER FEEDBACK:
{serializer.validated_data['feedback']}

PREVIOUS FEEDBACK HISTORY:
{chr(10).join(feedback_history[:-1]) if len(feedback_history) > 1 else 'First feedback'}

Please update the design plan based on the user's feedback. Only make the specified changes, keep other sections as they are. Return the updated plan in the same Markdown format.

If the user wants a new section added, place it in the appropriate location and add details.
If they want to modify an existing section, only update that part.
If they want a feature removed, remove that feature.

UPDATED PLAN:
"""

            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=update_prompt)],
                ),
            ]
            
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                # model="gemini-2.5-pro-preview-06-05",
                contents=contents,
                config=types.GenerateContentConfig(response_mime_type="text/plain"),
            )
            
            design_plan.current_plan = response.text.strip()
            design_plan.feedback_history = feedback_history
            design_plan.save()
            
            return Response({
                'plan_id': design_plan.id,
                'design_plan': response.text.strip(),
                'status': 'plan_updated'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.exception(f"Error updating plan: {str(e)}")
            return Response({
                'error': f"Failed to update plan: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    



    @action(detail=False, methods=['post'], url_path='approve-plan/(?P<plan_id>[^/.]+)')
    def approve_plan(self, request, plan_id=None):
        """Approve design plan and create website with NEW streamlined photo service"""
        
        logger.info(f"🎯 approve_plan called for plan_id: {plan_id}")
        
        try:
            design_plan = WebsiteDesignPlan.objects.get(id=plan_id, user=request.user)
            logger.info(f"📋 Design plan found: {design_plan.id}")
        except WebsiteDesignPlan.DoesNotExist:
            logger.error(f"❌ Design plan not found for id: {plan_id}")
            return Response({'error': 'Design plan not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            from spa.utils.color_utils import ColorHarmonySystem
            
            user_theme = design_plan.design_preferences.get('theme', 'light')
            primary_color = design_plan.design_preferences.get('primary_color', '#4B5EAA')
            
            # YENİ: Original prompt'u al
            original_prompt = design_plan.original_prompt
            logger.info(f"📝 Original prompt: {original_prompt[:100]}...")
            
            # YENİ STREAMLINED PHOTO GENERATION PIPELINE
            logger.info("🚀 Starting NEW streamlined photo generation...")
            
            try:
                # Step 1: Extract business context from original prompt
                business_context = asyncio.run(
                    direct_business_extractor.extract_business_context(original_prompt)
                )
                logger.info(f"✅ Business context: {business_context.get('business_type', 'unknown')}")
                
                # Step 2: Generate focused queries
                section_queries = focused_query_generator.generate_section_queries(
                    business_context, original_prompt
                )
                logger.info(f"✅ Generated queries for {len(section_queries)} sections")
                
                # Step 3: Get contextual photos
                context_images = asyncio.run(
                    streamlined_photo_service.get_contextual_photos(
                        business_context, section_queries
                    )
                )
                logger.info(f"✅ Retrieved {len(context_images)} contextual photos")
                
                image_generation_method = "STREAMLINED_FOCUSED_PIPELINE"
                
            except Exception as photo_error:
                logger.error(f"❌ Streamlined photo generation failed: {photo_error}")
                # Emergency fallback
                context_images = self._get_emergency_unsplash_images(original_prompt)
                image_generation_method = "EMERGENCY_FALLBACK"
            
            # Color Harmony System (mevcut kod - değişiklik yok)
            color_palette = ColorHarmonySystem.generate_accessible_colors(primary_color, user_theme)
            accessibility_check = ColorHarmonySystem.validate_accessibility(color_palette)
            
            # Accessibility optimization (mevcut kod - değişiklik yok)
            max_attempts = 3
            attempt = 0
            
            while not accessibility_check['is_accessible'] and attempt < max_attempts:
                attempt += 1
                logger.info(f"🔧 Adjusting colors for accessibility, attempt {attempt}")
                
                primary_rgb = ColorHarmonySystem.hex_to_rgb(primary_color)
                if user_theme == 'light':
                    adjusted_rgb = ColorHarmonySystem.adjust_brightness(primary_rgb, -0.2 * attempt)
                else:
                    adjusted_rgb = ColorHarmonySystem.adjust_brightness(primary_rgb, 0.2 * attempt)
                
                adjusted_primary = ColorHarmonySystem.rgb_to_hex(adjusted_rgb)
                color_palette = ColorHarmonySystem.generate_accessible_colors(adjusted_primary, user_theme)
                accessibility_check = ColorHarmonySystem.validate_accessibility(color_palette)

            # Enhanced prompt oluştur (mevcut kod - değişiklik yok)
            user_preferences = {
                "theme": user_theme,
                "primary_color": primary_color,
                "font_type": design_plan.design_preferences.get('heading_font', 'modern'),
                "website_prompt": design_plan.original_prompt,
                "business_type": business_context.get('business_type', 'general_business')  # YENİ
            }
            
            enhanced_prompt = generate_enhanced_prompt(
                design_plan=design_plan,
                context_images=context_images,
                user_preferences=user_preferences,
                color_palette=color_palette,
                accessibility_check=accessibility_check,
                image_generation_method=image_generation_method
            )
            
            # Gemini'ye gönder (mevcut kod - değişiklik yok)
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
                model="gemini-2.5-flash-preview-05-20",
                contents=contents,
                config=generate_content_config,
            )

            # Website objesi oluştur
            website_data = {
                'prompt': enhanced_prompt,
                'original_user_prompt': original_prompt,  # YENİ ALAN
                'business_context': business_context,  # YENİ ALAN
                'contact_email': design_plan.design_preferences.get('contact_email', ''),
                'primary_color': color_palette['primary'],
                'secondary_color': color_palette['secondary'],
                'accent_color': color_palette['accent'],
                'background_color': color_palette['background'],
                'theme': user_theme,
                'heading_font': design_plan.design_preferences.get('heading_font', 'Playfair Display'),
                'body_font': design_plan.design_preferences.get('body_font', 'Inter'),
                'corner_radius': design_plan.design_preferences.get('corner_radius', 8)
            }
            
            website_serializer = WebsiteCreateSerializer(data=website_data, context={'request': request})
            website_serializer.is_valid(raise_exception=True)
            website = website_serializer.save()
            
            # HTML içeriğini temizle (mevcut kod - değişiklik yok)
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
            
            logger.info(f"🎉 Website created successfully: {website.id}")
            
            return Response({
                'website_id': website.id,
                'status': 'website_created',
                'message': f'Website created with {image_generation_method}',
                'context_images': context_images,
                'business_context': business_context,  # YENİ
                'color_palette': color_palette,
                'accessibility_scores': accessibility_check['scores'],
                'image_generation_method': image_generation_method
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.exception(f"❌ Error creating website: {str(e)}")
            return Response({
                'error': f"Failed to create website: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def _validate_dynamic_images(self, images: Dict) -> bool:
        """Resimlerin gerçekten dinamik olup olmadığını kontrol et"""
        if not images or not isinstance(images, dict):
            return False
        
        # Picsum URL'leri varsa statik demektir
        for key, url in images.items():
            if url and 'picsum.photos' in url:
                logger.warning(f"❌ Static Picsum detected in {key}: {url}")
                return False
        
        # En az 2 geçerli URL olmalı
        valid_urls = sum(1 for url in images.values() 
                        if url and isinstance(url, str) and url.startswith(('http://', 'https://')))
        
        return valid_urls >= 2

    def _get_emergency_unsplash_images(self, prompt: str) -> Dict:
        """Acil durum için context-aware Unsplash resimleri"""
        simple_service = SimpleImageService()
        
        # Business type tespit et
        business_type = simple_service._detect_business_type(prompt)
        
        emergency_images = {}
        image_types = [
            ('hero_image', f'{business_type} professional workspace modern'),
            ('about_image', f'professional {business_type} portrait'),
            ('portfolio_1', f'{business_type} project showcase work'),
            ('portfolio_2', f'{business_type} creative solution'),
            ('portfolio_3', f'{business_type} innovation technology'),
            ('service_image', f'{business_type} service quality')
        ]
        
        for key, keywords in image_types:
            url = simple_service._get_unsplash_image(keywords)
            emergency_images[key] = url or f"https://images.unsplash.com/photo-149736621654?w=800&h=600&fit=crop&crop=center&q=80&auto=format"
        
        logger.info(f"🆘 Emergency images generated: {len(emergency_images)}")
        return emergency_images
    
    def _extract_business_type(self, prompt: str) -> str:
        """Prompt'tan iş türünü çıkar"""
        business_keywords = {
            'restaurant': ['restaurant', 'cafe', 'food', 'dining'],
            'tech': ['technology', 'software', 'app', 'digital'],
            'consulting': ['consulting', 'advisory', 'service'],
            'creative': ['design', 'creative', 'art', 'photography'],
            'healthcare': ['health', 'medical', 'clinic', 'wellness'],
            'education': ['education', 'school', 'course', 'learning'],
            'retail': ['shop', 'store', 'retail', 'product'],
            'finance': ['finance', 'bank', 'investment', 'money']
        }
        
        prompt_lower = prompt.lower()
        for business_type, keywords in business_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                return business_type
        
        return 'general business'
    
    def _calculate_hue_rotation(self, color: str) -> int:
        """Renk için hue rotation değeri hesapla"""
        # Basit bir implementasyon, geliştirilmeye açık
        return 0




    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        website = self.get_object()
        email = website.contact_email or website.user.email
        
        html_content = website.html_content
        
        # EmailJS keys'leri replace et
        html_content = html_content.replace('{{YOUR_EMAIL_JS_PUBLIC_KEY}}', settings.YOUR_EMAIL_JS_PUBLIC_KEY)
        html_content = html_content.replace('{{ YOUR_EMAIL_JS_PUBLIC_KEY }}', settings.YOUR_EMAIL_JS_PUBLIC_KEY)
        html_content = html_content.replace('YOUR_EMAIL_JS_PUBLIC_KEY', settings.YOUR_EMAIL_JS_PUBLIC_KEY)
        
        html_content = html_content.replace('{{YOUR_EMAIL_JS_SERVICE_ID}}', settings.YOUR_EMAIL_JS_SERVICE_ID)
        html_content = html_content.replace('{{ YOUR_EMAIL_JS_SERVICE_ID }}', settings.YOUR_EMAIL_JS_SERVICE_ID)
        html_content = html_content.replace('YOUR_EMAIL_JS_SERVICE_ID', settings.YOUR_EMAIL_JS_SERVICE_ID)
        
        html_content = html_content.replace('{{YOUR_EMAIL_JS_TEMPLATE_ID}}', settings.YOUR_EMAIL_JS_TEMPLATE_ID)
        html_content = html_content.replace('{{ YOUR_EMAIL_JS_TEMPLATE_ID }}', settings.YOUR_EMAIL_JS_TEMPLATE_ID)
        html_content = html_content.replace('YOUR_EMAIL_JS_TEMPLATE_ID', settings.YOUR_EMAIL_JS_TEMPLATE_ID)
        
        html_content = html_content.replace("USER_EMAIL_PLACEHOLDER", email)
        
        return Response({'html_content': html_content})
    

        
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request, pk=None):
        website = self.get_object()
        try:
            image_file = request.FILES.get('image')
            if not image_file:
                return Response({"error": "No image file provided"}, status=status.HTTP_400_BAD_REQUEST)
            title = request.data.get('title', image_file.name)
            uploaded_image = UploadedImage.objects.create(
                user=request.user,
                website=website,
                image=image_file,
                title=title
            )
            serializer = UploadedImageSerializer(uploaded_image, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception(f"Error uploading image: {str(e)}")
            return Response({
                'error': f"Failed to upload image: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def images(self, request, pk=None):
        website = self.get_object()
        images = UploadedImage.objects.filter(website=website, user=request.user)
        serializer = UploadedImageSerializer(images, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['put', 'patch'])
    def update_html(self, request, pk=None):
        try:
            website = self.get_object()
            website.html_content = request.data.get('html_content', website.html_content)
            website.save()
            return Response(WebsiteSerializer(website).data)
        except Exception as e:
            logger.exception(f"Error updating website HTML: {str(e)}")
            return Response({
                'error': f"Failed to update website HTML: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=True, methods=['post'])
    def update_element_style(self, request, pk=None):
        """Tek element stil güncelleme - CSS çakışması olmadan"""
        website = self.get_object()
        
        try:
            element_selector = request.data.get('element_selector')
            property_name = request.data.get('property')
            value = request.data.get('value')
            element_id = request.data.get('element_id', f'custom-{timezone.now().timestamp()}')
            
            # Custom styles JSON'ını güncelle
            custom_styles = website.custom_styles or {}
            
            if element_id not in custom_styles:
                custom_styles[element_id] = {}
            
            custom_styles[element_id][property_name] = value
            
            # Website'e kaydet
            website.custom_styles = custom_styles
            website.save(update_fields=['custom_styles'])
            
            logger.info(f"Style updated: {element_id} -> {property_name}: {value}")
            
            return Response({
                'success': True,
                'element_id': element_id,
                'property': property_name,
                'value': value
            })
            
        except Exception as e:
            logger.error(f"Style update error: {str(e)}")
            return Response({
                'error': f"Style update failed: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['post'])
    def update_element_content(self, request, pk=None):
        """Text content güncelleme endpoint'i"""
        website = self.get_object()
        
        try:
            element_id = request.data.get('element_id')
            content = request.data.get('content', '')
            
            # Element content mapping'ini tut
            element_contents = getattr(website, 'element_contents', {})
            if isinstance(element_contents, str):
                element_contents = json.loads(element_contents)
            
            element_contents[element_id] = content
            
            # Website'e kaydet (yeni alan gerekebilir)
            website.element_contents = element_contents
            website.save(update_fields=['element_contents'])
            
            logger.info(f"Content updated: {element_id} -> {content[:50]}...")
            
            return Response({
                'success': True,
                'element_id': element_id,
                'content': content
            })
            
        except Exception as e:
            logger.error(f"Content update error: {str(e)}")
            return Response({
                'error': f"Content update failed: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
  
    @action(detail=True, methods=['get'])
    def preview_with_styles(self, request, pk=None):
        """Custom styles ile preview - sadece görüntüleme için"""
        website = self.get_object()
        html_content = website.apply_all_customizations_safe()  # Safe version
        return Response({'html_content': html_content})