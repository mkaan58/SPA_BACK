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
from .base_html import BASE_HTML_TEMPLATE
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
    
    @action(detail=False, methods=['post'])
    def analyze_prompt(self, request):
        """Analyze user prompt and create detailed design plan"""
        serializer = AnalyzePromptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            design_prefs = {
                'primary_color': serializer.validated_data.get('primary_color', '#4B5EAA'),
                'theme': serializer.validated_data.get('theme', 'light'),
                'heading_font': serializer.validated_data.get('heading_font', 'Playfair Display'),
                'body_font': serializer.validated_data.get('body_font', 'Inter'),
                'corner_radius': serializer.validated_data.get('corner_radius', 8)
            }
            
            analyze_prompt = f"""
You are a senior UI/UX designer and frontend developer. Analyze the user's website request and create a DETAILED design plan.

USER REQUEST:
{serializer.validated_data['prompt']}

DESIGN PREFERENCES:
- Primary Color: {design_prefs['primary_color']}
- Theme: {design_prefs['theme']}
- Heading Font: {design_prefs['heading_font']}
- Body Font: {design_prefs['body_font']}
- Corner Radius: {design_prefs['corner_radius']}px

Create a detailed design plan in the following format:

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
                original_prompt=serializer.validated_data['prompt'],
                current_plan=response.text.strip(),
                design_preferences=design_prefs,
                feedback_history=[]
            )
            
            return Response({
                'plan_id': design_plan.id,
                'design_plan': response.text.strip(),
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
        """Approve design plan and create website with enhanced color harmony system"""
        try:
            design_plan = WebsiteDesignPlan.objects.get(id=plan_id, user=request.user)
        except WebsiteDesignPlan.DoesNotExist:
            return Response({'error': 'Design plan not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            from spa.utils.color_utils import ColorHarmonySystem
            
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            # Kullanıcının seçtiği tema ve primary color
            user_theme = design_plan.design_preferences.get('theme', 'light')
            primary_color = design_plan.design_preferences.get('primary_color', '#4B5EAA')
            
            # Otomatik renk harmonisi sistemi ile erişilebilir renk paleti oluştur
            color_palette = ColorHarmonySystem.generate_accessible_colors(primary_color, user_theme)
            
            # Erişilebilirlik kontrolü yap
            accessibility_check = ColorHarmonySystem.validate_accessibility(color_palette)
            
            # Eğer erişilebilirlik problemi varsa primary color'u otomatik ayarla
            max_attempts = 3
            attempt = 0
            
            while not accessibility_check['is_accessible'] and attempt < max_attempts:
                attempt += 1
                # Primary color'u ayarla
                primary_rgb = ColorHarmonySystem.hex_to_rgb(primary_color)
                if user_theme == 'light':
                    adjusted_rgb = ColorHarmonySystem.adjust_brightness(primary_rgb, -0.2 * attempt)
                else:
                    adjusted_rgb = ColorHarmonySystem.adjust_brightness(primary_rgb, 0.2 * attempt)
                
                adjusted_primary = ColorHarmonySystem.rgb_to_hex(adjusted_rgb)
                color_palette = ColorHarmonySystem.generate_accessible_colors(adjusted_primary, user_theme)
                accessibility_check = ColorHarmonySystem.validate_accessibility(color_palette)
            
# Geliştirilmiş prompt oluştur
# Geliştirilmiş prompt oluştur
            enhanced_prompt = f"""
APPROVED DESIGN PLAN:
{design_plan.current_plan}

ORIGINAL USER REQUEST:
{design_plan.original_prompt}

BASE TEMPLATE TO ENHANCE:
{BASE_HTML_TEMPLATE}

🎯 CRITICAL MISSION: Create a website exactly as described in the approved design plan with PERFECT visual accessibility and color harmony.

## 🧬 SCIENTIFICALLY CALCULATED COLOR SYSTEM

### WCAG AAA COMPLIANT COLOR PALETTE:
The following colors have been automatically calculated for maximum readability and visual harmony:

**Primary Colors:**
- Main Primary: {color_palette['primary']} (User's choice, accessibility optimized)
- Secondary: {color_palette['secondary']} (Harmonious analog color)
- Accent: {color_palette['accent']} (Complementary highlight color)

**Background & Surface Colors:**
- Main Background: {color_palette['background']}
- Card/Surface Background: {color_palette['card_background']}
- Border Color: {color_palette['border']}
- Border Hover: {color_palette['border_hover']}

**Text Colors (Perfect Contrast):**
- Primary Text: {color_palette['text_primary']} (Contrast: {accessibility_check['scores']['text_contrast']:.1f}:1)
- Secondary Text: {color_palette['text_secondary']}
- Muted Text: {color_palette['text_muted']}

**Interactive States:**
- Primary Hover: {color_palette['primary_hover']}
- Secondary Hover: {color_palette['secondary_hover']}

**System Colors:**
- Success: {color_palette['success']}
- Warning: {color_palette['warning']}
- Error: {color_palette['error']}
- Info: {color_palette['info']}

### ACCESSIBILITY VALIDATION RESULTS:
✅ Text Contrast Ratio: {accessibility_check['scores']['text_contrast']:.1f}:1 (WCAG AAA Standard: 7:1)
✅ Button Contrast Ratio: {accessibility_check['scores']['primary_contrast']:.1f}:1 (WCAG AA Standard: 4.5:1)
✅ Color Palette Status: {"FULLY ACCESSIBLE" if accessibility_check['is_accessible'] else "OPTIMIZED FOR ACCESSIBILITY"}

## 🔒 MANDATORY CSS COLOR SYSTEM IMPLEMENTATION

### 1. CSS Variables Setup (COPY EXACTLY):
```css
<style>
:root {{
  /* Primary Color System */
  --color-primary: {color_palette['primary']};
  --color-secondary: {color_palette['secondary']};
  --color-accent: {color_palette['accent']};
  
  /* Background System */
  --color-bg: {color_palette['background']};
  --color-card-bg: {color_palette['card_background']};
  
  /* Text System */
  --color-text-primary: {color_palette['text_primary']};
  --color-text-secondary: {color_palette['text_secondary']};
  --color-text-muted: {color_palette['text_muted']};
  
  /* Border System */
  --color-border: {color_palette['border']};
  --color-border-hover: {color_palette['border_hover']};
  
  /* Interactive States */
  --color-primary-hover: {color_palette['primary_hover']};
  --color-secondary-hover: {color_palette['secondary_hover']};
  
  /* Status Colors */
  --color-success: {color_palette['success']};
  --color-warning: {color_palette['warning']};
  --color-error: {color_palette['error']};
  --color-info: {color_palette['info']};
  
  /* Design System */
  --border-radius: {design_plan.design_preferences.get('corner_radius', 8)}px;
  --font-heading: '{design_plan.design_preferences.get('heading_font', 'Playfair Display')}', serif;
  --font-body: '{design_plan.design_preferences.get('body_font', 'Inter')}', sans-serif;
}}

/* 🎯 GUARANTEED VISIBILITY BASE STYLES */
* {{
  box-sizing: border-box;
}}

body {{
  background-color: var(--color-bg) !important;
  color: var(--color-text-primary) !important;
  font-family: var(--font-body) !important;
  line-height: 1.6 !important;
  margin: 0 !important;
  padding: 0 !important;
}}

/* 🔴 CRITICAL: BUTTON SYSTEM (ZERO TOLERANCE FOR INVISIBLE BUTTONS) */
.btn-primary {{
  background-color: var(--color-primary) !important;
  color: var(--color-bg) !important;
  border: 2px solid var(--color-primary) !important;
  font-weight: 600 !important;
  padding: 12px 24px !important;
  border-radius: var(--border-radius) !important;
  transition: all 0.2s ease !important;
  text-decoration: none !important;
  display: inline-block !important;
  cursor: pointer !important;
  font-size: 16px !important;
  min-height: 44px !important;
  min-width: 44px !important;
}}

.btn-primary:hover {{
  background-color: var(--color-primary-hover) !important;
  border-color: var(--color-primary-hover) !important;
  color: var(--color-bg) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
}}

.btn-secondary {{
  background-color: transparent !important;
  color: var(--color-primary) !important;
  border: 2px solid var(--color-primary) !important;
  font-weight: 600 !important;
  padding: 12px 24px !important;
  border-radius: var(--border-radius) !important;
  transition: all 0.2s ease !important;
  text-decoration: none !important;
  display: inline-block !important;
  cursor: pointer !important;
  font-size: 16px !important;
  min-height: 44px !important;
  min-width: 44px !important;
}}

.btn-secondary:hover {{
  background-color: var(--color-primary) !important;
  color: var(--color-bg) !important;
  border-color: var(--color-primary) !important;
}}

/* 🔴 CRITICAL: NAVIGATION SYSTEM */
.navbar {{
  background-color: var(--color-bg) !important;
  border-bottom: 1px solid var(--color-border) !important;
  backdrop-filter: blur(10px) !important;
  padding: 16px 0 !important;
  position: sticky !important;
  top: 0 !important;
  z-index: 1000 !important;
}}

.navbar-brand {{
  color: var(--color-text-primary) !important;
  font-weight: 700 !important;
  font-family: var(--font-heading) !important;
  font-size: 24px !important;
  text-decoration: none !important;
}}

.navbar-nav .nav-link {{
  color: var(--color-text-secondary) !important;
  font-weight: 500 !important;
  padding: 8px 16px !important;
  border-radius: calc(var(--border-radius) / 2) !important;
  transition: all 0.2s ease !important;
  text-decoration: none !important;
  display: block !important;
}}

.navbar-nav .nav-link:hover {{
  color: var(--color-primary) !important;
  background-color: var(--color-card-bg) !important;
}}

.navbar-toggler {{
  border: 2px solid var(--color-border) !important;
  color: var(--color-text-primary) !important;
  background: transparent !important;
  padding: 8px 12px !important;
}}

/* 🔴 CRITICAL: FORM SYSTEM */
.form-control {{
  background-color: var(--color-bg) !important;
  border: 2px solid var(--color-border) !important;
  color: var(--color-text-primary) !important;
  border-radius: var(--border-radius) !important;
  padding: 12px 16px !important;
  font-size: 16px !important;
  width: 100% !important;
  transition: all 0.2s ease !important;
}}

.form-control:focus {{
  border-color: var(--color-primary) !important;
  box-shadow: 0 0 0 3px rgba(75, 94, 170, 0.1) !important;
  outline: none !important;
}}

.form-control::placeholder {{
  color: var(--color-text-muted) !important;
  opacity: 1 !important;
}}

.form-label {{
  color: var(--color-text-primary) !important;
  font-weight: 600 !important;
  margin-bottom: 8px !important;
  display: block !important;
}}

/* 🔴 CRITICAL: CARD SYSTEM */
.card {{
  background-color: var(--color-card-bg) !important;
  border: 1px solid var(--color-border) !important;
  color: var(--color-text-primary) !important;
  border-radius: var(--border-radius) !important;
  transition: all 0.3s ease !important;
  overflow: hidden !important;
}}

.card:hover {{
  border-color: var(--color-border-hover) !important;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1) !important;
  transform: translateY(-4px) !important;
}}

.card-title {{
  color: var(--color-text-primary) !important;
  font-family: var(--font-heading) !important;
  font-weight: 700 !important;
  margin-bottom: 12px !important;
}}

.card-text {{
  color: var(--color-text-secondary) !important;
  line-height: 1.6 !important;
}}

/* 🔴 CRITICAL: ICON SYSTEM */
.icon {{
  color: var(--color-primary) !important;
  transition: color 0.2s ease !important;
}}

.icon:hover {{
  color: var(--color-primary-hover) !important;
}}

/* 🔴 CRITICAL: LINK SYSTEM */
a {{
  color: var(--color-primary) !important;
  text-decoration: underline !important;
  text-underline-offset: 2px !important;
  transition: all 0.2s ease !important;
}}

a:hover {{
  color: var(--color-primary-hover) !important;
  text-decoration: none !important;
}}

/* 🔴 CRITICAL: HEADING HIERARCHY */
h1, h2, h3, h4, h5, h6 {{
  color: var(--color-text-primary) !important;
  font-family: var(--font-heading) !important;
  font-weight: 700 !important;
  line-height: 1.2 !important;
  margin-bottom: 16px !important;
}}

h1 {{ font-size: 3rem !important; }}
h2 {{ font-size: 2.5rem !important; }}
h3 {{ font-size: 2rem !important; }}
h4 {{ font-size: 1.5rem !important; }}
h5 {{ font-size: 1.25rem !important; }}
h6 {{ font-size: 1rem !important; }}

/* 🔴 CRITICAL: RESPONSIVE TEXT SCALING */
@media (max-width: 768px) {{
  h1 {{ font-size: 2rem !important; }}
  h2 {{ font-size: 1.75rem !important; }}
  h3 {{ font-size: 1.5rem !important; }}
  h4 {{ font-size: 1.25rem !important; }}
}}

/* 🔴 CRITICAL: UTILITY CLASSES */
.text-primary {{ color: var(--color-text-primary) !important; }}
.text-secondary {{ color: var(--color-text-secondary) !important; }}
.text-muted {{ color: var(--color-text-muted) !important; }}
.bg-primary {{ background-color: var(--color-primary) !important; }}
.bg-card {{ background-color: var(--color-card-bg) !important; }}
.border-primary {{ border-color: var(--color-primary) !important; }}

/* 🔴 CRITICAL: FOCUS STATES FOR ACCESSIBILITY */
button:focus,
input:focus,
textarea:focus,
select:focus,
a:focus {{
  outline: 2px solid var(--color-primary) !important;
  outline-offset: 2px !important;
}}

/* 🔴 CRITICAL: HOVER STATES FOR INTERACTIVE ELEMENTS */
button,
.btn,
[role="button"] {{
  cursor: pointer !important;
  transition: all 0.2s ease !important;
}}

button:hover,
.btn:hover,
[role="button"]:hover {{
  transform: translateY(-1px) !important;
}}
</style>
```

## 🚨 CRITICAL IMPLEMENTATION RULES

### 1. ZERO TOLERANCE POLICIES:
- ❌ NEVER use any color not in the provided palette
- ❌ NEVER create invisible buttons, links, or icons
- ❌ NEVER use text that blends with backgrounds
- ❌ NEVER ignore hover states
- ❌ NEVER use hardcoded colors like #ffffff, #000000, etc.

### 2. MANDATORY ELEMENT CHECKS:
- ✅ Every button must have minimum 44px touch target
- ✅ Every text must pass 7:1 contrast ratio (WCAG AAA)
- ✅ Every interactive element must have hover/focus states
- ✅ Every icon must be clearly visible
- ✅ Every form field must be properly labeled

### 3. RESPONSIVE REQUIREMENTS:
- ✅ Mobile-first design (320px minimum width)
- ✅ Touch-friendly interface (44px minimum touch targets)
- ✅ Readable text at 200% zoom
- ✅ Working navigation on all screen sizes

## 🎨 DESIGN SYSTEM SPECIFICATIONS

### Typography System:
- **Headings**: {design_plan.design_preferences.get('heading_font', 'Playfair Display')} with color: var(--color-text-primary)
- **Body Text**: {design_plan.design_preferences.get('body_font', 'Inter')} with color: var(--color-text-secondary)
- **Labels/Captions**: var(--color-text-muted) for less important text

### Spacing System (Use consistently):
- **Extra Small**: 4px
- **Small**: 8px
- **Medium**: 16px
- **Large**: 24px
- **Extra Large**: 32px
- **XXL**: 48px

### Animation Guidelines:
- **Duration**: 200ms for micro-interactions, 300ms for cards/sections
- **Easing**: ease-in-out for natural movement
- **Hover Effects**: Subtle scale (1.02x) and shadow increases
- **Focus**: Clear outline with 2px solid primary color

## 📱 CRITICAL MOBILE RESPONSIVENESS FIXES

### MANDATORY MOBILE FIXES (COPY EXACTLY):
```css
/* 🔴 CRITICAL: MOBILE NAVIGATION FIX */
.mobile-menu {{
  position: fixed !important;
  top: 64px !important;
  right: 0 !important;
  height: calc(100vh - 64px) !important;
  width: 280px !important;
  background-color: var(--color-bg) !important;
  border-left: 1px solid var(--color-border) !important;
  transform: translateX(100%) !important;
  transition: transform 0.3s ease !important;
  z-index: 999 !important;
  overflow-y: auto !important;
}}

.mobile-menu.active {{
  transform: translateX(0) !important;
}}

.hamburger {{
  display: flex !important;
  flex-direction: column !important;
  justify-content: space-around !important;
  width: 24px !important;
  height: 24px !important;
  background: transparent !important;
  border: none !important;
  cursor: pointer !important;
  padding: 0 !important;
}}

.hamburger span {{
  display: block !important;
  width: 100% !important;
  height: 2px !important;
  background-color: var(--color-text-primary) !important;
  transition: all 0.3s ease !important;
  transform-origin: center !important;
}}

.hamburger.active span:nth-child(1) {{
  transform: rotate(45deg) translate(5px, 5px) !important;
}}

.hamburger.active span:nth-child(2) {{
  opacity: 0 !important;
}}

.hamburger.active span:nth-child(3) {{
  transform: rotate(-45deg) translate(7px, -6px) !important;
}}

/* 🔴 CRITICAL: MOBILE TOUCH TARGETS */
@media (max-width: 768px) {{
  .btn-primary,
  .btn-secondary {{
    min-height: 48px !important;
    min-width: 48px !important;
    padding: 16px 24px !important;
    font-size: 16px !important;
  }}
  
  .nav-link {{
    padding: 16px 20px !important;
    font-size: 16px !important;
    display: block !important;
    border-bottom: 1px solid var(--color-border) !important;
  }}
  
  .card {{
    margin-bottom: 20px !important;
  }}
}}

/* 🔴 CRITICAL: MOBILE FORM FIXES */
@media (max-width: 768px) {{
  .form-control {{
    font-size: 16px !important;
    padding: 16px !important;
    min-height: 48px !important;
  }}
  
  textarea.form-control {{
    min-height: 120px !important;
  }}
}}
```

## 🚀 ADVANCED INTERACTIVE FEATURES - NEW CDN INTEGRATIONS

### 1. SWIPER.JS IMPLEMENTATION (PREMIUM SLIDERS & CAROUSELS)

**MANDATORY CDN SETUP:**
```html
<!-- In HEAD section -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css">

<!-- Before closing BODY tag -->
<script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
```

**When to Use Swiper (AUTO-DETECT):**
- Portfolio section with 4+ items → Convert to elegant responsive slider
- Services section with 3+ cards → Touch-enabled carousel
- Testimonials section → Auto-playing testimonial showcase
- Team members → Professional team carousel
- Image galleries → Touch-friendly gallery slider

**PORTFOLIO SWIPER TEMPLATE (COPY EXACTLY - MOBILE OPTIMIZED):**
```html
<div class="swiper portfolio-swiper">
  <div class="swiper-wrapper">
    <div class="swiper-slide">
      <div class="portfolio-item">
        <img src="portfolio-image.jpg" alt="Project" class="portfolio-image">
        <div class="portfolio-overlay">
          <h3 class="portfolio-title">Project Title</h3>
          <p class="portfolio-description">Brief description</p>
          <a href="#" class="portfolio-link btn-primary">View Project</a>
        </div>
      </div>
    </div>
    <!-- More slides -->
  </div>
  <div class="swiper-pagination"></div>
  <div class="swiper-button-next"></div>
  <div class="swiper-button-prev"></div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {{
  const portfolioSwiper = new Swiper('.portfolio-swiper', {{
    slidesPerView: 1,
    spaceBetween: 20,
    loop: true,
    autoplay: {{
      delay: 4000,
      disableOnInteraction: false,
      pauseOnMouseEnter: true,
    }},
    pagination: {{
      el: '.swiper-pagination',
      clickable: true,
      dynamicBullets: true,
    }},
    navigation: {{
      nextEl: '.swiper-button-next',
      prevEl: '.swiper-button-prev',
    }},
    breakpoints: {{
      320: {{
        slidesPerView: 1,
        spaceBetween: 15,
      }},
      640: {{
        slidesPerView: 2,
        spaceBetween: 20,
      }},
      1024: {{
        slidesPerView: 3,
        spaceBetween: 30,
      }},
    }},
    effect: 'slide',
    speed: 600,
    touchRatio: 1,
    threshold: 5,
    allowTouchMove: true,
    // Mobile optimizations
    preventInteractionOnTransition: false,
    watchOverflow: true,
    centerInsufficientSlides: true,
  }});
}});
</script>
```

**SWIPER STYLING (USE COLOR VARIABLES - MOBILE OPTIMIZED):**
```css
.swiper {{
  padding: 20px 0 60px 0 !important;
  overflow: visible !important;
}}

.swiper-pagination {{
  bottom: 10px !important;
  left: 50% !important;
  transform: translateX(-50%) !important;
}}

.swiper-pagination-bullet {{
  background-color: var(--color-text-muted) !important;
  opacity: 0.5 !important;
  width: 10px !important;
  height: 10px !important;
  margin: 0 4px !important;
  transition: all 0.3s ease !important;
}}

.swiper-pagination-bullet-active {{
  background-color: var(--color-primary) !important;
  opacity: 1 !important;
  transform: scale(1.3) !important;
}}

/* Mobile Navigation Buttons */
@media (min-width: 768px) {{
  .swiper-button-next,
  .swiper-button-prev {{
    color: var(--color-primary) !important;
    background-color: var(--color-bg) !important;
    width: 44px !important;
    height: 44px !important;
    border-radius: 50% !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
    transition: all 0.3s ease !important;
    border: 2px solid var(--color-border) !important;
  }}

  .swiper-button-next:hover,
  .swiper-button-prev:hover {{
    background-color: var(--color-primary) !important;
    color: var(--color-bg) !important;
    transform: scale(1.1) !important;
    border-color: var(--color-primary) !important;
  }}

  .swiper-button-next:after,
  .swiper-button-prev:after {{
    font-size: 14px !important;
    font-weight: bold !important;
  }}
}}

/* Hide navigation buttons on mobile */
@media (max-width: 767px) {{
  .swiper-button-next,
  .swiper-button-prev {{
    display: none !important;
  }}
  
  .swiper-pagination {{
    bottom: 20px !important;
  }}
}}
```

### 2. TYPED.JS IMPLEMENTATION (DYNAMIC TEXT ANIMATIONS)

**MANDATORY CDN SETUP:**
```html
<!-- Before closing BODY tag -->
<script src="https://cdn.jsdelivr.net/npm/typed.js@2.1.0/dist/typed.umd.js"></script>
```

**When to Use Typed.js (AUTO-IMPLEMENT):**
- Hero section main title → Dynamic typing effect
- Professional titles → Job role rotation
- Skills showcase → Skill names appearing dynamically
- Call-to-action text → Engaging message typing

**HERO TYPED IMPLEMENTATION (COPY EXACTLY):**
```html
<div class="hero-section">
  <h1 class="hero-title">
    I'm a <span id="typed-text" class="typed-element"></span>
  </h1>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {{
  const typedElement = document.getElementById('typed-text');
  if (typedElement) {{
    new Typed('#typed-text', {{
      strings: [
        'Web Developer',
        'UI/UX Designer', 
        'Problem Solver',
        'Creative Thinker'
      ],
      typeSpeed: 80,
      backSpeed: 50,
      backDelay: 2000,
      startDelay: 500,
      loop: true,
      showCursor: true,
      cursorChar: '|',
      autoInsertCss: true,
    }});
  }}
}});
</script>
```

**TYPED.JS STYLING (USE COLOR VARIABLES):**
```css
.typed-element {{
  color: var(--color-primary) !important;
  font-weight: 700 !important;
  position: relative !important;
}}

.typed-cursor {{
  color: var(--color-primary) !important;
  font-weight: 300 !important;
  animation: blink 1s infinite !important;
}}

@keyframes blink {{
  0%, 50% {{ opacity: 1; }}
  51%, 100% {{ opacity: 0; }}
}}
```

### 3. PARTICLES.JS IMPLEMENTATION (DYNAMIC BACKGROUND EFFECTS)

**MANDATORY CDN SETUP:**
```html
<!-- Before closing BODY tag -->
<script src="https://cdn.jsdelivr.net/npm/particles.js@2.0.0/particles.min.js"></script>
```

**When to Use Particles.js (SMART IMPLEMENTATION):**
- Hero section background → Subtle floating particles
- About section → Gentle background animation
- Contact section → Interactive particle field

**HERO PARTICLES IMPLEMENTATION (COPY EXACTLY):**
```html
<div id="particles-js" class="particles-container"></div>

<script>
document.addEventListener('DOMContentLoaded', function() {{
  if (typeof particlesJS !== 'undefined') {{
    particlesJS('particles-js', {{
      particles: {{
        number: {{
          value: 50,
          density: {{
            enable: true,
            value_area: 800
          }}
        }},
        color: {{
          value: '{color_palette['primary']}'
        }},
        shape: {{
          type: 'circle',
          stroke: {{
            width: 0,
            color: '{color_palette['primary']}'
          }}
        }},
        opacity: {{
          value: 0.3,
          random: true,
          anim: {{
            enable: true,
            speed: 1,
            opacity_min: 0.1,
            sync: false
          }}
        }},
        size: {{
          value: 3,
          random: true,
          anim: {{
            enable: true,
            speed: 2,
            size_min: 0.1,
            sync: false
          }}
        }},
        line_linked: {{
          enable: true,
          distance: 150,
          color: '{color_palette['primary']}',
          opacity: 0.2,
          width: 1
        }},
        move: {{
          enable: true,
          speed: 1,
          direction: 'none',
          random: false,
          straight: false,
          out_mode: 'out',
          bounce: false
        }}
      }},
      interactivity: {{
        detect_on: 'canvas',
        events: {{
          onhover: {{
            enable: true,
            mode: 'repulse'
          }},
          onclick: {{
            enable: true,
            mode: 'push'
          }},
          resize: true
        }},
        modes: {{
          grab: {{
            distance: 140,
            line_linked: {{
              opacity: 1
            }}
          }},
          bubble: {{
            distance: 400,
            size: 40,
            duration: 2,
            opacity: 8,
            speed: 3
          }},
          repulse: {{
            distance: 100,
            duration: 0.4
          }},
          push: {{
            particles_nb: 4
          }},
          remove: {{
            particles_nb: 2
          }}
        }}
      }},
      retina_detect: true
    }});
  }}
}});
</script>
```

**PARTICLES STYLING (RESPONSIVE & ACCESSIBLE - MOBILE OPTIMIZED):**
```css
.particles-container {{
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  width: 100% !important;
  height: 100% !important;
  z-index: -1 !important;
  pointer-events: none !important;
}}

#particles-js {{
  position: absolute !important;
  width: 100% !important;
  height: 100% !important;
  background-color: transparent !important;
}}

/* CRITICAL: Mobile optimization - disable particles */
@media (max-width: 768px) {{
  .particles-container {{
    display: none !important;
  }}
}}

/* CRITICAL: Reduced motion accessibility */
@media (prefers-reduced-motion: reduce) {{
  .particles-container {{
    display: none !important;
  }}
}}

/* CRITICAL: Performance optimization for low-end devices */
@media (max-width: 1024px) and (max-height: 768px) {{
  .particles-container {{
    display: none !important;
  }}
}}
```

## 🎯 SMART INTEGRATION RULES

### CONDITIONAL IMPLEMENTATION:
1. **Portfolio Section Detection:**
   - IF portfolio has 4+ items → Implement Swiper slider
   - ELSE → Keep standard grid layout

2. **Hero Section Detection:**
   - IF hero has title/subtitle → Add Typed.js effect
   - IF hero is full-screen → Add Particles.js background

3. **Performance Optimization:**
   - Mobile devices → Disable particles for better performance
   - Reduced motion preference → Disable all animations
   - Touch devices → Enable touch-friendly swiper controls

### MANDATORY CDN LOADING ORDER (MOBILE OPTIMIZED):
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
  
  <!-- Performance optimized CDN loading -->
  <script src="https://cdn.tailwindcss.com"></script>
  
  <!-- Critical CSS -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <link href="https://fonts.googleapis.com/css2?family={design_plan.design_preferences.get('heading_font', 'Playfair Display').replace(' ', '+')}:wght@400;700&family={design_plan.design_preferences.get('body_font', 'Inter').replace(' ', '+')}:wght@400;700&display=swap" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.css" rel="stylesheet">
  
  <!-- Advanced CDNs -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css">
  
  <!-- EmailJS -->
  <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/@emailjs/browser@4/dist/email.min.js"></script>
  <script>
    if (typeof emailjs !== 'undefined') {{
      emailjs.init("{{{{YOUR_EMAIL_JS_PUBLIC_KEY}}}}");
    }}
  </script>
</head>
<body x-data="{{
  mobileMenuOpen: false,
  darkMode: localStorage.getItem('darkMode') === 'true' || (!localStorage.getItem('darkMode') && window.matchMedia('(prefers-color-scheme: dark)').matches),
  showBackToTop: false
}}" x-init="
  if (darkMode) document.documentElement.classList.add('dark');
  $watch('darkMode', value => {{
    if (value) {{
      document.documentElement.classList.add('dark');
      localStorage.setItem('darkMode', 'true');
    }} else {{
      document.documentElement.classList.remove('dark');
      localStorage.setItem('darkMode', 'false');
    }}
  }});
  
  window.addEventListener('scroll', () => {{
    showBackToTop = window.scrollY > 300;
  }});
">

  <!-- Website content with EXACT mobile menu structure -->
  <nav class="fixed top-0 left-0 right-0 z-50 bg-white/90 dark:bg-gray-900/90 backdrop-blur-md border-b border-gray-200 dark:border-gray-700">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <!-- Logo -->
        <div class="flex-shrink-0">
          <a href="#home" class="font-heading text-2xl font-bold" style="color: var(--color-primary)">
            Brand Name
          </a>
        </div>
        
        <!-- Desktop Navigation -->
        <div class="hidden md:block">
          <div class="ml-10 flex items-baseline space-x-8">
            <a href="#home" class="nav-link" style="color: var(--color-text-primary)">Home</a>
            <a href="#about" class="nav-link" style="color: var(--color-text-secondary)">About</a>
            <a href="#portfolio" class="nav-link" style="color: var(--color-text-secondary)">Portfolio</a>
            <a href="#contact" class="nav-link" style="color: var(--color-text-secondary)">Contact</a>
          </div>
        </div>
        
        <!-- Mobile menu button -->
        <div class="md:hidden">
          <button @click="mobileMenuOpen = !mobileMenuOpen" class="hamburger" :class="{{{{ 'active': mobileMenuOpen }}}}" aria-label="Toggle menu">
            <span></span>
            <span></span>
            <span></span>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Mobile Navigation -->
    <div class="mobile-menu md:hidden" :class="{{{{ 'active': mobileMenuOpen }}}}">
      <div class="px-4 py-2">
        <a href="#home" @click="mobileMenuOpen = false" class="nav-link block">Home</a>
        <a href="#about" @click="mobileMenuOpen = false" class="nav-link block">About</a>
        <a href="#portfolio" @click="mobileMenuOpen = false" class="nav-link block">Portfolio</a>
        <a href="#contact" @click="mobileMenuOpen = false" class="nav-link block">Contact</a>
      </div>
    </div>
  </nav>

  <!-- Content sections... -->

  <!-- JavaScript CDNs (EXACT ORDER) -->
  <script src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
  <script src="https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/typed.js@2.1.0/dist/typed.umd.js"></script>
  
  <!-- Only load particles on desktop -->
  <script>
    if (window.innerWidth > 768 && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {{
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/particles.js@2.0.0/particles.min.js';
      document.body.appendChild(script);
    }}
  </script>
  
  <!-- Initialize everything -->
  <script>
    // Initialize AOS
    AOS.init({{
      duration: 600,
      easing: 'ease-out',
      once: true,
      offset: 50,
      disable: function() {{
        return window.innerWidth < 768;
      }}
    }});
    
    // Mobile menu close on outside click
    document.addEventListener('click', function(event) {{
      const mobileMenu = document.querySelector('.mobile-menu');
      const hamburger = document.querySelector('.hamburger');
      const navbar = document.querySelector('nav');
      
      if (!navbar.contains(event.target) && !hamburger.contains(event.target)) {{
        // Use Alpine.js to close menu
        if (window.Alpine) {{
          Alpine.store('mobileMenuOpen', false);
        }}
      }}
    }});
    
    // Prevent zoom on input focus (iOS fix)
    document.querySelectorAll('input, textarea, select').forEach(element => {{
      element.addEventListener('touchstart', function() {{
        if (element.style.fontSize !== '16px') {{
          element.style.fontSize = '16px';
        }}
      }});
    }});
  </script>
</body>
</html>
```

## 📋 FINAL IMPLEMENTATION CHECKLIST

Before delivering the HTML, ensure:
1. ✅ All colors use CSS variables from the provided palette
2. ✅ All buttons are clearly visible and functional
3. ✅ All text is readable with proper contrast
4. ✅ All icons are visible and appropriately colored
5. ✅ All hover states provide clear feedback
6. ✅ All forms are functional with proper validation
7. ✅ Navigation works on mobile and desktop
8. ✅ Contact form uses EmailJS exactly as in BASE_HTML_TEMPLATE, MAKE SURE you've added contact form in website.
9. ✅ Responsive design works on all screen sizes
10. ✅ Professional, modern, and accessible appearance
11. ✅ **NEW:** Swiper sliders work on touch devices
12. ✅ **NEW:** Typed.js animations are smooth and professional
13. ✅ **NEW:** Particles.js effects are subtle and performance-optimized
14. ✅ **NEW:** All advanced features are mobile-responsive
15. ✅ **NEW:** Accessibility preferences are respected (reduced motion)
16. ✅ **CRITICAL:** Hamburger menu opens/closes properly on mobile
17. ✅ **CRITICAL:** Touch targets are minimum 44px on mobile
18. ✅ **CRITICAL:** Text is readable at 16px minimum on mobile
19. ✅ **CRITICAL:** Forms work properly on mobile devices
20. ✅ **CRITICAL:** No horizontal scrolling on any screen size

TECHNOLOGIES TO USE:
- Tailwind CSS (CDN: https://cdn.tailwindcss.com) + Custom CSS Variables
- Alpine.js (CDN: https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js)
- AOS (CDN: https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.js)
- Font Awesome (CDN: https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css)
- Google Fonts: {design_plan.design_preferences.get('heading_font', 'Playfair Display')} + {design_plan.design_preferences.get('body_font', 'Inter')}
- **NEW:** Swiper.js (CDN: https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css + https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js)
- **NEW:** Typed.js (CDN: https://cdn.jsdelivr.net/npm/typed.js@2.1.0/dist/typed.umd.js)
- **NEW:** Particles.js (CDN: https://cdn.jsdelivr.net/npm/particles.js@2.0.0/particles.min.js)

### CRITICAL: EMAILJS CONTACT FORM
Use EXACTLY the contact form structure from BASE_HTML_TEMPLATE. Do NOT modify:
- Form field names and IDs
- JavaScript event handling logic  
- EmailJS sendForm implementation
- Placeholder replacement strings

Generate a complete, production-ready HTML file that implements the approved design plan with perfect visual accessibility AND advanced interactive features.
Every element must be clearly visible, properly contrasted, fully functional, and enhanced with premium interactive effects.

Deliver only clean HTML code starting with <!DOCTYPE html>. No markdown, no explanations - just flawless, premium-quality code.
"""
            
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
            
            # HTML içeriğini temizle
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
            
            return Response({
                'website_id': website.id,
                'status': 'website_created',
                'message': 'Website successfully created with enhanced color harmony system',
                'color_palette': color_palette,
                'accessibility_scores': accessibility_check['scores']
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.exception(f"Error creating website from plan: {str(e)}")
            return Response({
                'error': f"Failed to create website: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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