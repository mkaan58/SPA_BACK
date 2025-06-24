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
from spa.api.permissions import CanAccessWebsite, CanCreateWebsite, get_user_plan_info
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
from spa.tasks import *
from .pagination import StandardResultsSetPagination  # Import pagination

import asyncio
import json

# Mevcut import'ların altına ekle
from spa.services.direct_business_extractor import get_direct_business_extractor
from spa.services.focused_query_generator import get_focused_query_generator
from spa.services.streamlined_photo_service import get_streamlined_photo_service
from asgiref.sync import sync_to_async
from typing import Dict, List

import json
import html

logger = logging.getLogger(__name__)

# Base HTML Template - Modern Website with all features

# spa/api/views.py - Line-Based AI Editor

import logging
import json
import re
import time

# Configure logger for better debugging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create handler if it doesn't exist
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class LineBasedAIEditor:
    """Line-based AI editing system for precise website modifications"""
    
    def __init__(self):
        self.html_lines = []
        self.line_map = {}
        

    def prepare_line_context(self, html_content, user_request):
        """Prepare smart line-numbered HTML context for AI"""
        
        # Split HTML into lines
        self.html_lines = html_content.split('\n')
        
        # Create line mapping with numbers
        numbered_html = ""
        for i, line in enumerate(self.html_lines, 1):
            numbered_html += f"{i:4d}: {line}\n"
        
        # Quick structure analysis
        structure_info = self._analyze_html_structure()
        
        ai_prompt = f"""
    You are an expert HTML/CSS editor with structural awareness. You understand component relationships and never break functional structures.

    USER REQUEST: "{user_request}"

    STRUCTURAL OVERVIEW:
    {structure_info}

    HTML WITH LINE NUMBERS:
    {numbered_html}

    CRITICAL INTELLIGENCE RULES:
    1. DETECT COMPONENTS: Identify sliders, modals, forms, sections before making changes
    2. PRESERVE STRUCTURES: Never break container-wrapper-item hierarchies
    3. SAFE DELETION: When removing items, only remove the item itself, not its container
    4. PATTERN RECOGNITION: Understand common patterns (Swiper sliders, Bootstrap modals, etc.)
    5. VALIDATE CHANGES: Ensure your changes don't break functionality

    COMPONENT AWARENESS:
    - Swiper Sliders: Container > Wrapper > Slides + Navigation + Pagination
    - Modals: Trigger > Modal Container > Content
    - Forms: Form Tag > Field Groups > Individual Fields
    - Sections: Section Tag > Content Blocks

    SMART EXAMPLES:

    Request: "Remove last project from portfolio"
    → THINK: This is likely a slider/carousel. Find the last slide item only, preserve navigation.
    → ACTION: Remove last <div class="swiper-slide">...</div> completely, keep wrapper intact.

    Request: "Delete contact form"  
    → THINK: User wants form gone, but preserve section structure.
    → ACTION: Remove form content, keep section container.

    Request: "Fix modal not showing"
    → THINK: Modal JavaScript issue, check triggers and IDs.
    → ACTION: Fix modal attributes, ensure proper linking.

    STRUCTURAL SAFETY CHECK:
    Before responding, mentally verify:
    - Will containers remain intact?
    - Will navigation/pagination still work?
    - Are there any orphaned closing tags?
    - Does the change make structural sense?

    REQUIRED JSON FORMAT:
    {{
      "analysis": "What you understood and what component you're modifying",
      "structural_impact": "What structures this change affects",
      "line_changes": [
        {{
          "start_line": 123,
          "end_line": 125, 
          "reason": "Specific reason for this exact change",
          "new_content": "Precise replacement content or empty string for deletion"
        }}
      ],
      "summary": "Brief summary of changes and structural preservation"
    }}

    RESPOND WITH VALID JSON ONLY. NO MARKDOWN. NO EXPLANATIONS OUTSIDE JSON.
    """
        
        return ai_prompt

    def _analyze_html_structure(self):
        """Analyze HTML structure for AI context"""
        structure = {
            'sections': [],
            'forms': [],
            'scripts': [],
            'total_lines': len(self.html_lines)
        }
        
        current_section = None
        in_script = False
        in_form = False
        
        for i, line in enumerate(self.html_lines, 1):
            line_clean = line.strip()
            
            # Detect sections
            if re.search(r'<(section|div)[^>]*id=["\']([^"\']*)["\']', line_clean):
                match = re.search(r'id=["\']([^"\']*)["\']', line_clean)
                if match:
                    section_id = match.group(1)
                    structure['sections'].append({
                        'id': section_id,
                        'start_line': i,
                        'type': 'section'
                    })
            
            # Detect forms
            if '<form' in line_clean:
                match = re.search(r'id=["\']([^"\']*)["\']', line_clean)
                form_id = match.group(1) if match else f'form_line_{i}'
                structure['forms'].append({
                    'id': form_id,
                    'start_line': i,
                    'type': 'form'
                })
                in_form = True
            elif '</form>' in line_clean and in_form:
                if structure['forms']:
                    structure['forms'][-1]['end_line'] = i
                in_form = False
            
            # Detect scripts
            if '<script' in line_clean:
                structure['scripts'].append({
                    'start_line': i,
                    'type': 'script'
                })
                in_script = True
            elif '</script>' in line_clean and in_script:
                if structure['scripts']:
                    structure['scripts'][-1]['end_line'] = i
                in_script = False
        
        # Format structure info for AI
        info = f"Total Lines: {structure['total_lines']}\n"
        info += f"Sections Found: {len(structure['sections'])}\n"
        
        for section in structure['sections']:
            info += f"  - {section['id']}: starts at line {section['start_line']}\n"
        
        info += f"Forms Found: {len(structure['forms'])}\n"
        for form in structure['forms']:
            end_info = f" to {form.get('end_line', '?')}" if 'end_line' in form else ""
            info += f"  - {form['id']}: lines {form['start_line']}{end_info}\n"
        
        info += f"Script Blocks: {len(structure['scripts'])}\n"
        for script in structure['scripts']:
            end_info = f" to {script.get('end_line', '?')}" if 'end_line' in script else ""
            info += f"  - Script: lines {script['start_line']}{end_info}\n"
        
        return info
    
    def apply_line_changes(self, line_changes):
        """Apply line-based changes to HTML content"""
        
        if not line_changes:
            return '\n'.join(self.html_lines)
        
        # Sort changes by start_line in reverse order (from bottom to top)
        # This prevents line number shifts from affecting subsequent changes
        sorted_changes = sorted(line_changes, key=lambda x: x['start_line'], reverse=True)
        
        modified_lines = self.html_lines.copy()
        
        for change in sorted_changes:
            start_line = change['start_line'] - 1  # Convert to 0-based index
            end_line = change['end_line'] - 1      # Convert to 0-based index
            new_content = change['new_content']
            
            # Validate line numbers
            if start_line < 0 or end_line >= len(modified_lines):
                logger.error(f"Invalid line range: {start_line+1} to {end_line+1}")
                continue
            
            if start_line > end_line:
                logger.error(f"Invalid line range: start ({start_line+1}) > end ({end_line+1})")
                continue
            
            # ✅ DÜZELTME: Boş content kontrolü
            if new_content is None or new_content == "":
                # Gerçek silme işlemi - hiç satır ekleme
                new_lines = []
            else:
                # ✅ DÜZELTME: strip() ile boş satırları temizle
                new_lines = [line for line in new_content.split('\n')]
                # Sadece tamamen boş content'te boş array döndür
                if len(new_lines) == 1 and new_lines[0].strip() == "":
                    new_lines = []
            
            # Replace the specified line range with new content
            # Remove old lines and insert new ones
            del modified_lines[start_line:end_line+1]
            
            # Insert new lines
            for i, new_line in enumerate(new_lines):
                modified_lines.insert(start_line + i, new_line)
            
            logger.info(f"✅ Applied change: lines {start_line+1}-{end_line+1} → {len(new_lines)} new lines")
        
        return '\n'.join(modified_lines)



class WebsiteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination  # Pagination ekleyin  
    permission_classes = [IsAuthenticated, CanAccessWebsite]  

    def get_permissions(self):
        """
        View'e göre farklı permission'lar uygula
        """
        if self.action in ['create', 'analyze_prompt', 'approve_plan']:
            # Website creation action'ları için CanCreateWebsite permission'ı ekle
            permission_classes = [IsAuthenticated, CanCreateWebsite]
        else:
            # Diğer action'lar için standart permission'lar
            permission_classes = [IsAuthenticated, CanAccessWebsite]
        
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """
        Website oluşturma - permission kontrolü ile
        """
        # Permission kontrolü otomatik yapılır, ama manuel kontrol de yapabilirsin
        perms = [permission() for permission in self.get_permissions()]
        
        for perm in perms:
            if not perm.has_permission(request, self):
                # Eğer limit aşıldıysa özel mesaj döndür
                if hasattr(request, 'limit_exceeded') and request.limit_exceeded:
                    limit_details = getattr(request, 'limit_details', {})
                    subscription_type = limit_details.get('subscription_type', 'free')
                    current_count = limit_details.get('current_count', 0)
                    max_websites = limit_details.get('max_websites', 2)
                    
                    # Plan önerisi mesajları
                    upgrade_messages = {
                        'free': "Upgrade to Basic (5 websites) or Premium (20 websites) to create more!",
                        'basic': "Upgrade to Premium (20 websites) to create more!"
                    }
                    
                    error_message = f"You've reached your {subscription_type} plan limit of {max_websites} websites."
                    upgrade_message = upgrade_messages.get(subscription_type, "")
                    
                    if upgrade_message:
                        error_message += f" {upgrade_message}"
                    
                    return Response({
                        "error": error_message,
                        "limit_exceeded": True,
                        "subscription_type": subscription_type,
                        "current_count": current_count,
                        "max_websites": max_websites,
                        "upgrade_required": subscription_type != 'premium'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # Diğer permission hataları
                return Response({
                    "error": "You don't have permission to perform this action."
                }, status=status.HTTP_403_FORBIDDEN)
        
        # Permission geçtiyse normal create işlemi
        return super().create(request, *args, **kwargs)

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
        """Analyze user prompt and create detailed design plan - BACKGROUND VERSION"""
        serializer = AnalyzePromptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        limit_details = getattr(request, 'limit_details', {})
        from spa.tasks import analyze_prompt_task
        try:
            # Start background task immediately
            task = analyze_prompt_task.apply_async(
                args=[request.data, request.user.id]
            )
            
            logger.info(f"🚀 analyze_prompt task started: {task.id} for user {request.user.id}")
            
            # Get task result (this will wait for completion)
            result = task.get(timeout=120)  # Wait max 2 minutes
            
            if result.get('success'):
                return Response({
                    'plan_id': result['plan_id'],
                    'design_plan': result['design_plan'],
                    'status': result['status'],
                    'user_limits': limit_details  # Kullanıcının limit bilgilerini ekle
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'error': result.get('error', 'Task failed')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            logger.exception(f"❌ Error in analyze_prompt: {str(e)}")
            return Response({
                'error': f"Failed to analyze prompt: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def user_plan_info(self, request):
        """
        Kullanıcının plan bilgilerini döndürür
        """
        plan_info = get_user_plan_info(request.user)
        
        return Response({
            'plan_info': plan_info,
            'checkout_urls': {
                'basic': settings.LEMON_SQUEEZY_CHECKOUT_URL_BASIC,
                'premium': settings.LEMON_SQUEEZY_CHECKOUT_URL_PREMIUM
            }
        })


    @action(detail=False, methods=['post'], url_path='update-plan/(?P<plan_id>[^/.]+)')
    def update_plan(self, request, plan_id=None):
        """Update design plan based on user feedback - BACKGROUND VERSION"""
        try:
            design_plan = WebsiteDesignPlan.objects.get(id=plan_id, user=request.user)
        except WebsiteDesignPlan.DoesNotExist:
            return Response({'error': 'Design plan not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UpdatePlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        from spa.tasks import update_plan_task
        try:
            # Start background task
            task = update_plan_task.apply_async(
                args=[plan_id, serializer.validated_data['feedback'], request.user.id]
            )
            
            logger.info(f"🚀 update_plan task started: {task.id} for plan {plan_id}")
            
            # Get task result (wait for completion)
            result = task.get(timeout=90)  # Wait max 1.5 minutes
            
            if result.get('success'):
                return Response({
                    'plan_id': result['plan_id'],
                    'design_plan': result['design_plan'],
                    'status': result['status']
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': result.get('error', 'Task failed')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            logger.exception(f"❌ Error in update_plan: {str(e)}")
            return Response({
                'error': f"Failed to update plan: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def ai_line_edit(self, request, pk=None):
        """Line-based AI editing endpoint - BACKGROUND VERSION"""
        website = self.get_object()
        
        try:
            user_request = request.data.get('user_request', '').strip()
            if not user_request:
                return Response({
                    'error': 'User request is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"🤖 AI Line Edit task starting: {user_request[:100]}...")
            
            # Start background task
            task = ai_line_edit_task.apply_async(
                args=[website.id, user_request, request.user.id]
            )
            
            logger.info(f"🚀 ai_line_edit task started: {task.id} for website {website.id}")
            
            # Get task result (wait for completion)
            result = task.get(timeout=150)  # Wait max 2.5 minutes
            
            if result.get('success'):
                return Response({
                    'success': True,
                    'modified_html': result['modified_html'],
                    'analysis': result['analysis'],
                    'changes_applied': result['changes_applied'],
                    'summary': result['summary'],
                    'html_actually_changed': result['html_actually_changed'],
                    'original_html_length': result['original_html_length'],
                    'modified_html_length': result['modified_html_length'],
                    'database_save_verified': True
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': result.get('error', 'AI edit task failed'),
                    'user_request': user_request[:100]
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            logger.exception(f"❌ Error in ai_line_edit: {str(e)}")
            return Response({
                'error': f'Line-based AI edit failed: {str(e)}',
                'user_request': user_request[:100] if 'user_request' in locals() else 'Unknown'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    



    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request, pk=None):
        """Upload and process image - BACKGROUND VERSION"""
        website = self.get_object()
        
        try:
            image_file = request.FILES.get('image')
            if not image_file:
                return Response({
                    "error": "No image file provided"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            title = request.data.get('title', image_file.name)
            
            # Prepare image data for task
            image_data = {
                'image_file': image_file
            }
            
            metadata = {
                'title': title
            }
            
            logger.info(f"🖼️ Image upload task starting: {image_file.name}")
            
            # Start background task
            task = upload_image_task.apply_async(
                args=[image_data, metadata, request.user.id, website.id]
            )
            
            logger.info(f"🚀 upload_image task started: {task.id} for website {website.id}")
            
            # Get task result (wait for completion)
            result = task.get(timeout=120)  # Wait max 2 minutes
            
            if result.get('success'):
                # Create response in same format as original
                uploaded_image = UploadedImage.objects.get(id=result['image_id'])
                serializer = UploadedImageSerializer(uploaded_image, context={'request': request})
                
                return Response({
                    **serializer.data,
                    'processing_info': {
                        'optimized': result.get('optimized', False),
                        'file_size': result.get('file_size', 0)
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'error': result.get('error', 'Image upload failed')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.exception(f"❌ Error uploading image: {str(e)}")
            return Response({
                'error': f"Failed to upload image: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Update the approve_plan method to use background photo generation

    @action(detail=False, methods=['post'])
    def extract_business_context(self, request):
        """Extract business context from prompt - BACKGROUND VERSION"""
        
        prompt = request.data.get('prompt', '').strip()
        if not prompt:
            return Response({
                'error': 'Prompt is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create cache key for this prompt
            import hashlib
            cache_key = f"business_context_{hashlib.md5(prompt.encode()).hexdigest()}"
            
            # Start background task
            task = extract_business_context_task.apply_async(
                args=[prompt, request.user.id, cache_key]
            )
            
            logger.info(f"🧠 extract_business_context task started: {task.id}")
            
            # Get task result (wait for completion)
            result = task.get(timeout=60)  # Wait max 1 minute
            
            if result.get('success'):
                return Response({
                    'success': True,
                    'business_context': result['business_context'],
                    'source': result['source'],
                    'confidence': result['business_context'].get('confidence', 0.5)
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': result.get('error', 'Business context extraction failed')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.exception(f"❌ Error extracting business context: {str(e)}")
            return Response({
                'error': f"Failed to extract business context: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # NEW METHOD: Generate color palette endpoint
    @action(detail=False, methods=['post'])
    def generate_color_palette(self, request):
        """Generate accessible color palette - BACKGROUND VERSION"""
        
        primary_color = request.data.get('primary_color', '#4B5EAA')
        theme = request.data.get('theme', 'light')
        
        # Validate inputs
        if not re.match(r'^#[0-9A-Fa-f]{6}$', primary_color):
            return Response({
                'error': 'Invalid primary color format (use #RRGGBB)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if theme not in ['light', 'dark']:
            return Response({
                'error': 'Theme must be either "light" or "dark"'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create cache key
            cache_key = f"color_palette_{primary_color}_{theme}_{request.user.id}"
            
            # Start background task
            task = generate_color_palette_task.apply_async(
                args=[primary_color, theme, request.user.id, cache_key]
            )
            
            logger.info(f"🎨 generate_color_palette task started: {task.id}")
            
            # Get task result (wait for completion)
            result = task.get(timeout=30)  # Wait max 30 seconds
            
            if result.get('success'):
                return Response({
                    'success': True,
                    'color_palette': result['color_palette'],
                    'accessibility_check': result['accessibility_check'],
                    'source': result['source'],
                    'optimization_info': result.get('optimization_info', {})
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': result.get('error', 'Color palette generation failed')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.exception(f"❌ Error generating color palette: {str(e)}")
            return Response({
                'error': f"Failed to generate color palette: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # @action(detail=False, methods=['post'], url_path='approve-plan/(?P<plan_id>[^/.]+)')
    # def approve_plan(self, request, plan_id=None):
    #     """
    #     ENHANCED approve_plan - Uses background business intelligence tasks
    #     """
        
    #     try:
    #         design_plan = WebsiteDesignPlan.objects.get(id=plan_id, user=request.user)
    #     except WebsiteDesignPlan.DoesNotExist:
    #         return Response({'error': 'Design plan not found'}, status=status.HTTP_404_NOT_FOUND)
        
    #     try:
    #         user_theme = design_plan.design_preferences.get('theme', 'light')
    #         primary_color = design_plan.design_preferences.get('primary_color', '#4B5EAA')
    #         original_prompt = design_plan.original_prompt
            
    #         logger.info(f"📋 Enhanced approve_plan starting for: {plan_id}")
            
    #         # STEP 1: Extract business context in background
    #         logger.info("🧠 Starting background business context extraction...")
            
    #         import hashlib
    #         context_cache_key = f"business_context_{hashlib.md5(original_prompt.encode()).hexdigest()}"
            
    #         context_task = extract_business_context_task.apply_async(
    #             args=[original_prompt, request.user.id, context_cache_key]
    #         )
            
    #         # STEP 2: Generate color palette in background
    #         logger.info("🎨 Starting background color palette generation...")
            
    #         palette_cache_key = f"color_palette_{primary_color}_{user_theme}_{request.user.id}"
            
    #         palette_task = generate_color_palette_task.apply_async(
    #             args=[primary_color, user_theme, request.user.id, palette_cache_key]
    #         )
            
    #         # STEP 3: Get results from background tasks
    #         logger.info("⏳ Waiting for background tasks to complete...")
            
    #         # Get business context result
    #         context_result = context_task.get(timeout=90)
    #         if context_result.get('success'):
    #             business_context = context_result['business_context']
    #             logger.info(f"✅ Business context: {business_context.get('business_type', 'unknown')}")
    #         else:
    #             logger.error(f"Business context extraction failed: {context_result.get('error')}")
    #             business_context = {'business_type': 'general_business', 'original_prompt': original_prompt}
            
    #         # Get color palette result
    #         palette_result = palette_task.get(timeout=60)
    #         if palette_result.get('success'):
    #             color_palette = palette_result['color_palette']
    #             accessibility_check = palette_result['accessibility_check']
    #             logger.info(f"✅ Color palette generated: {palette_result['source']}")
    #         else:
    #             logger.error(f"Color palette generation failed: {palette_result.get('error')}")
    #             # Fallback to existing color system
    #             from spa.utils.color_utils import ColorHarmonySystem
    #             color_palette = ColorHarmonySystem.generate_accessible_colors(primary_color, user_theme)
    #             accessibility_check = ColorHarmonySystem.validate_accessibility(color_palette)
            
    #         # STEP 4: Generate photos in background
    #         logger.info("🖼️ Starting background photo generation...")
            
    #         photo_task = generate_photos_task.apply_async(
    #             args=[business_context, {}, request.user.id, plan_id]
    #         )
            
    #         # Get photo results
    #         photo_result = photo_task.get(timeout=180)  # Wait max 3 minutes
            
    #         if photo_result.get('success'):
    #             context_images = photo_result['context_images']
    #             image_generation_method = photo_result['generation_method']
    #             logger.info(f"✅ Photos generated: {len(context_images)} images")
    #         else:
    #             logger.error(f"Photo generation failed: {photo_result.get('error')}")
    #             # Use emergency fallback
    #             context_images = self._get_emergency_unsplash_images(original_prompt)
    #             image_generation_method = "emergency_fallback"
            
    #         # STEP 5: Continue with rest of approve_plan logic (same as before)
    #         user_preferences = {
    #             "theme": user_theme,
    #             "primary_color": primary_color,
    #             "font_type": design_plan.design_preferences.get('heading_font', 'modern'),
    #             "website_prompt": design_plan.original_prompt,
    #             "business_type": business_context.get('business_type', 'general_business')
    #         }
            
    #         # Generate enhanced prompt (same as before)
    #         from spa.api.approve_plan_prompt import generate_enhanced_prompt
            
    #         enhanced_prompt = generate_enhanced_prompt(
    #             design_plan=design_plan,
    #             context_images=context_images,
    #             user_preferences=user_preferences,
    #             color_palette=color_palette,
    #             accessibility_check=accessibility_check,
    #             image_generation_method=image_generation_method
    #         )
            
    #         # Send to Gemini (same as before)
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

    #         # Create website (same as before)
    #         website_data = {
    #             'prompt': enhanced_prompt,
    #             'original_user_prompt': original_prompt,
    #             'business_context': business_context,
    #             'contact_email': design_plan.design_preferences.get('contact_email', ''),
    #             'primary_color': color_palette['primary'],
    #             'secondary_color': color_palette['secondary'],
    #             'accent_color': color_palette['accent'],
    #             'background_color': color_palette['background'],
    #             'theme': user_theme,
    #             'heading_font': design_plan.design_preferences.get('heading_font', 'Playfair Display'),
    #             'body_font': design_plan.design_preferences.get('body_font', 'Inter'),
    #             'corner_radius': design_plan.design_preferences.get('corner_radius', 8)
    #         }
            
    #         website_serializer = WebsiteCreateSerializer(data=website_data, context={'request': request})
    #         website_serializer.is_valid(raise_exception=True)
    #         website = website_serializer.save()
            
    #         # Process HTML content (same as before)
    #         content = response.text.strip()
            
    #         if content.startswith("```html") and "```" in content[6:]:
    #             content = content.replace("```html", "", 1)
    #             content = content.rsplit("```", 1)[0].strip()
    #         elif content.startswith("```") and content.endswith("```"):
    #             content = content[3:-3].strip()
            
    #         if not content.startswith("<!DOCTYPE") and not content.startswith("<html"):
    #             content = f"<!DOCTYPE html>\n<html>\n<head>\n<meta charset=\"UTF-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n<title>Generated Website</title>\n</head>\n<body>\n{content}\n</body>\n</html>"
            
    #         website.html_content = content
    #         website.save()
            
    #         design_plan.is_approved = True
    #         design_plan.save()
            
    #         logger.info(f"🎉 Website created successfully: {website.id}")
            
    #         return Response({
    #             'website_id': website.id,
    #             'status': 'website_created',
    #             'message': f'Website created with {image_generation_method}',
    #             'context_images': context_images,
    #             'business_context': business_context,
    #             'color_palette': color_palette,
    #             'accessibility_scores': accessibility_check['scores'],
    #             'image_generation_method': image_generation_method,
    #             'processing_info': {
    #                 'business_context_source': context_result.get('source', 'unknown'),
    #                 'color_palette_source': palette_result.get('source', 'unknown'),
    #                 'photo_generation_method': image_generation_method
    #             }
    #         }, status=status.HTTP_201_CREATED)
            
    #     except Exception as e:
    #         logger.exception(f"❌ Error creating website: {str(e)}")
    #         return Response({
    #             'error': f"Failed to create website: {str(e)}"
    #         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    # views.py - TAMAMEN DEĞİŞTİR
    @action(detail=False, methods=['post'], url_path='approve-plan/(?P<plan_id>[^/.]+)')
    def approve_plan(self, request, plan_id=None):
        """Background approve_plan with task monitoring"""
        
        try:
            design_plan = WebsiteDesignPlan.objects.get(id=plan_id, user=request.user)
        except WebsiteDesignPlan.DoesNotExist:
            return Response({'error': 'Design plan not found'}, status=status.HTTP_404_NOT_FOUND)
        
        limit_details = getattr(request, 'limit_details', {})
        try:
            # 🚀 Background task başlat
            from spa.tasks import create_website_optimized
            
            task = create_website_optimized.apply_async(
                args=[plan_id, request.user.id]
            )
            
            logger.info(f"🚀 Website creation task started: {task.id} for plan {plan_id}")
            
            # ✅ Task ID'yi döndür - Frontend'in beklediği format
            return Response({
                'status': 'processing',
                'task_id': task.id,
                'message': 'Website creation started in background',
                'plan_id': plan_id,
                'remaining_websites': limit_details.get('remaining', 0)
            }, status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            logger.exception(f"❌ Error starting website creation: {str(e)}")
            return Response({
                'error': f"Failed to start website creation: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='task-status/(?P<task_id>[^/.]+)')
    def task_status(self, request, task_id=None):
        """Check task status - SAME RESULTS when completed"""
        from celery.result import AsyncResult
        
        result = AsyncResult(task_id)
        
        if result.state == 'PENDING':
            return Response({'status': 'processing', 'progress': 'Generating website...'})
        elif result.state == 'SUCCESS':
            data = result.result
            return Response({
                'status': 'completed',
                'website_id': data['website_id'],
                'business_context': data['business_context'],
                'context_images': data['context_images'],
                'color_palette': data['color_palette'],
                'image_generation_method': data['image_generation_method'],
                'processing_time': data['processing_time']
            })
        elif result.state == 'FAILURE':
            return Response({
                'status': 'failed',
                'error': str(result.info)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'status': result.state.lower()})

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
    

    # Add this to check API key
    def _check_gemini_setup(self):
        """Check if Gemini API is properly configured"""
        if not hasattr(settings, 'GEMINI_API_KEY') or not settings.GEMINI_API_KEY:
            logger.error("❌ GEMINI_API_KEY not configured in settings")
            return False
        
        if settings.GEMINI_API_KEY == 'your-gemini-api-key-here':
            logger.error("❌ GEMINI_API_KEY is placeholder value")
            return False
        
        return True




# views.py'ye bu kapsamlı versiyonu koy:


    @action(detail=True, methods=['get'])
    def debug_html_content(self, request, pk=None):
        """Debug endpoint to check current HTML content"""
        website = self.get_object()
        
        html_lines = website.html_content.split('\n')
        
        # Find title tag
        title_line = next((line for line in html_lines if '<title>' in line.lower()), 'No title found')
        
        # Extract title content if found
        title_content = 'No title'
        if '<title>' in title_line.lower():
            try:
                import re
                title_match = re.search(r'<title[^>]*>(.*?)</title>', title_line, re.IGNORECASE)
                if title_match:
                    title_content = title_match.group(1).strip()
            except:
                title_content = 'Title extraction failed'
        
        # Get meta description if exists
        meta_description = next((line for line in html_lines if 'meta' in line.lower() and 'description' in line.lower()), 'No meta description')
        
        # Count common HTML elements
        element_counts = {
            'divs': website.html_content.count('<div'),
            'sections': website.html_content.count('<section'),
            'headers': website.html_content.count('<header'),
            'footers': website.html_content.count('<footer'),
            'images': website.html_content.count('<img'),
            'links': website.html_content.count('<a '),
            'buttons': website.html_content.count('<button'),
            'forms': website.html_content.count('<form'),
        }
        
        return Response({
            'website_id': website.id,
            'title': website.title if hasattr(website, 'title') else 'No title field',
            'html_length': len(website.html_content),
            'total_lines': len(html_lines),
            'first_10_lines': html_lines[:10],
            'last_10_lines': html_lines[-10:],
            'title_tag': title_line[:100] + '...' if len(title_line) > 100 else title_line,
            'title_content': title_content,
            'meta_description': meta_description[:100] + '...' if len(meta_description) > 100 else meta_description,
            'element_counts': element_counts,
            'html_preview': {
                'starts_with': website.html_content[:200],
                'ends_with': website.html_content[-200:],
            },
            'last_modified': getattr(website, 'updated_at', 'Unknown'),
            'character_encoding_check': {
                'has_utf8_meta': 'charset=utf-8' in website.html_content.lower() or 'charset="utf-8"' in website.html_content.lower(),
                'has_viewport': 'viewport' in website.html_content.lower(),
                'has_doctype': website.html_content.strip().startswith('<!DOCTYPE'),
            }
        })
    

    @action(detail=True, methods=['post'])
    def add_custom_domain(self, request, pk=None):
        """Custom domain ekle"""
        website = self.get_object()
        
        # Permission check
        if website.user != request.user:
            return Response({
                'success': False,
                'error': 'Bu website\'e erişim yetkiniz yok'
            }, status=status.HTTP_403_FORBIDDEN)
        
        domain_name = request.data.get('domain_name', '').strip().lower()
        
        if not domain_name:
            return Response({
                'success': False,
                'error': 'Domain adı gerekli'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Basit domain formatı kontrolü
        domain_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.[a-zA-Z]{2,}$'
        if not re.match(domain_pattern, domain_name):
            return Response({
                'success': False,
                'error': 'Geçersiz domain formatı (örn: ornek.com)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Domain service'i kullan
        service = SimpleDomainService()
        result = service.add_custom_domain(website.id, domain_name)
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def verify_custom_domain(self, request, pk=None):
        """Custom domain doğrula"""
        website = self.get_object()
        
        # Permission check
        if website.user != request.user:
            return Response({
                'success': False,
                'error': 'Bu website\'e erişim yetkiniz yok'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Domain service'i kullan
        service = SimpleDomainService()
        result = service.verify_domain(website.id)
        
        return Response(result)

    @action(detail=True, methods=['delete'])
    def remove_custom_domain(self, request, pk=None):
        """Custom domain kaldır"""
        website = self.get_object()
        
        # Permission check
        if website.user != request.user:
            return Response({
                'success': False,
                'error': 'Bu website\'e erişim yetkiniz yok'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Domain service'i kullan
        service = SimpleDomainService()
        result = service.remove_domain(website.id)
        
        return Response(result)

    @action(detail=False, methods=['get'])
    def check_domain_availability(self, request):
        """Domain müsaitlik kontrolü (opsiyonel)"""
        domain_name = request.query_params.get('domain_name', '').strip().lower()
        
        if not domain_name:
            return Response({
                'success': False,
                'error': 'Domain adı gerekli'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Sadece bizim sistemimizde kullanılıp kullanılmadığını kontrol et
        is_taken = Website.objects.filter(custom_domain=domain_name).exists()
        
        return Response({
            'success': True,
            'domain': domain_name,
            'available': not is_taken,
            'message': 'Domain müsait' if not is_taken else 'Domain zaten kullanımda'
        })
    

def check_user_can_create_website(user):
    """
    Kullanıcının website oluşturup oluşturamayacağını kontrol eder
    """
    plan_info = get_user_plan_info(user)
    return plan_info['remaining']['websites'] > 0

def get_upgrade_suggestion(user):
    """
    Kullanıcı için upgrade önerisi döndürür
    """
    subscription_type = user.subscription_type
    
    suggestions = {
        'free': {
            'message': 'Upgrade to Basic for 5 websites or Premium for 20 websites!',
            'plans': ['basic', 'premium']
        },
        'basic': {
            'message': 'Upgrade to Premium for 20 websites!',
            'plans': ['premium']
        },
        'premium': {
            'message': 'You are already on the highest plan!',
            'plans': []
        }
    }
    
    return suggestions.get(subscription_type, suggestions['free'])