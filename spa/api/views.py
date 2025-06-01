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

logger = logging.getLogger(__name__)

# Base HTML Template - Modern Website with all features


class WebsiteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Website.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        return WebsiteSerializer
    

    
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
        """Approve design plan and create website"""
        try:
            design_plan = WebsiteDesignPlan.objects.get(id=plan_id, user=request.user)
        except WebsiteDesignPlan.DoesNotExist:
            return Response({'error': 'Design plan not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            # Get user's chosen theme
            user_theme = design_plan.design_preferences.get('theme', 'light')
            
            design_preferences = (
                f"SOLID DESIGN SYSTEM - {user_theme.upper()} THEME ONLY:\n"
                f"- **Primary Color**: {design_plan.design_preferences['primary_color']}\n"
                f"- **Theme**: {user_theme.capitalize()} theme - CREATE ONLY THIS THEME, no theme switching\n"
                f"- **Color Strategy**: Design everything specifically for {user_theme} theme with perfect readability\n"
                f"- **Typography**: Use Google Fonts: Heading font: {design_plan.design_preferences['heading_font']}, Body font: {design_plan.design_preferences['body_font']}\n"
                f"- **Corner Radius**: Apply {design_plan.design_preferences['corner_radius']}px to all rounded elements\n"
            )
            
            enhanced_prompt = f"""
    APPROVED DESIGN PLAN:
    {design_plan.current_plan}

    DESIGN PREFERENCES:
    {design_plan.design_preferences}

    ORIGINAL USER REQUEST:
    {design_plan.original_prompt}

    BASE TEMPLATE TO ENHANCE:
    {BASE_HTML_TEMPLATE}

    Create a website exactly as described in the approved design plan above. Implement every detail from the plan without missing anything.

    You are a senior frontend developer creating a modern, luxurious, and fully responsive website. Generate a complete HTML file with all features working perfectly.

    CRITICAL REQUIREMENTS:

    1. **Use the base template above as your foundation** - enhance it according to the approved design plan
    2. **Implement exactly what's described in the approved design plan**
    3. **Replace placeholder content** with relevant, realistic content (no lorem ipsum)
    4. **Ensure full responsiveness** - perfect on mobile, tablet, desktop. Everything should look proper for all devices (navbar, footer, hero section, custom sections etc.)
    5. **Working JavaScript** - all buttons, forms, animations must function
    6. **SINGLE THEME ONLY** - Create ONLY {user_theme} theme, no theme toggle functionality
    7. **Smooth navigation** - working anchor links with proper scroll padding
    8. **Contact form** - Alpine.js validation with success messages
    9. **Portfolio section** - real Unsplash images with hover effects
    10. **Modern animations** - AOS scroll animations and CSS transitions
    11. **Social media links** - working external links with proper href attributes
    12. **No zoom functionality for gallery/portfolio section** - use only hover effects for images

    13. **SOLID {user_theme.upper()} THEME STYLING SYSTEM:**

        **Perfect Readability Requirements:**
        - **Text Contrast**: Every single text element must be easily readable
        - **Button Clarity**: All buttons must have clear, readable text with proper contrast
        - **Link Visibility**: All links must be clearly distinguishable and readable
        - **Card Elements**: All card content must be perfectly readable
        - **Form Elements**: All form labels, inputs, and placeholders must be clear
        - **Navigation**: All navigation elements must be highly visible and readable
        - **Hover States**: All hover effects must maintain readability while providing clear feedback

        **For {user_theme.capitalize()} Theme Specific Rules:**
        """

            if user_theme == 'light':
                enhanced_prompt += """
        **LIGHT THEME IMPLEMENTATION:**
        - **Background Colors**: Use white (#ffffff) and light grays (#f8fafc, #f1f5f9, #e2e8f0)
        - **Text Colors**: Use dark colors for maximum readability:
        - Primary text: #1f2937 (gray-800) or #111827 (gray-900)
        - Secondary text: #374151 (gray-700) or #4b5563 (gray-600)
        - Muted text: #6b7280 (gray-500)
        - **Primary Color Usage**: Use user's primary color ({design_plan.design_preferences['primary_color']}) for:
        - Buttons (with white or very dark text for contrast)
        - Links and highlights
        - Borders and accents
        - Icon colors where appropriate
        - **Card Backgrounds**: Use white or very light gray (#f9fafb)
        - **Border Colors**: Use light grays (#e5e7eb, #d1d5db)
        - **Shadow Effects**: Use subtle gray shadows for depth
        - **Hover Effects**: Darken backgrounds slightly, increase shadows
        """
            else:
                enhanced_prompt += """
        **DARK THEME IMPLEMENTATION:**
        - **Background Colors**: Use dark colors (#0f172a, #1e293b, #334155)
        - **Text Colors**: Use light colors for maximum readability:
        - Primary text: #f8fafc (slate-50) or #ffffff
        - Secondary text: #e2e8f0 (slate-200) or #cbd5e1 (slate-300)
        - Muted text: #94a3b8 (slate-400)
        - **Primary Color Usage**: Use user's primary color ({design_plan.design_preferences['primary_color']}) for:
        - Buttons (with white or very dark text for contrast)
        - Links and highlights
        - Borders and accents
        - Icon colors where appropriate
        - **Card Backgrounds**: Use dark gray (#1e293b, #334155)
        - **Border Colors**: Use dark grays (#475569, #64748b)
        - **Shadow Effects**: Use darker shadows with slight opacity
        - **Hover Effects**: Lighten backgrounds slightly, add glow effects
        """

            enhanced_prompt += f"""

    14. **UNIVERSAL READABILITY STANDARDS:**
        - **Minimum Contrast Ratio**: 4.5:1 for normal text, 7:1 for better accessibility
        - **Font Sizes**: Ensure all text is large enough to read easily
        - **Interactive Elements**: Clear visual feedback on hover and focus states
        - **Color Dependencies**: Never rely only on color to convey information
        - **Focus Indicators**: Clear focus outlines for keyboard navigation

    15. **SPECIFIC ELEMENT STYLING FOR {user_theme.upper()} THEME:**
        - **Navigation Bar**: Solid background with high contrast text
        - **Buttons**: Primary color background with contrasting text
        - **Form Inputs**: Clear borders, readable placeholder text, proper focus states
        - **Cards**: Consistent background with proper text contrast
        - **Links**: Clearly distinguishable from regular text
        - **Headings**: High contrast, hierarchical sizing
        - **Body Text**: Perfect readability with appropriate line height

    DESIGN REQUIREMENTS:
    {design_preferences}

    TECHNOLOGIES TO USE:
    - Tailwind CSS (CDN: https://cdn.tailwindcss.com)
    - Alpine.js (CDN: https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js)
    - AOS (CDN: https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.js)
    - Font Awesome (CDN: https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css)
    - Google Fonts: {design_plan.design_preferences['heading_font']} + {design_plan.design_preferences['body_font']}

    CONTENT GUIDELINES:
    - Use realistic, professional content related to the website description
    - Include 6-8 portfolio items with real Unsplash images
    - Add appropriate social media links (Twitter, LinkedIn, GitHub, etc.)
    - Ensure all text is human-readable and relevant to the site purpose
    - Use proper alt texts for accessibility

    TECHNICAL REQUIREMENTS:
    - All JavaScript in <script> tags at the end of <body>
    - Only styles and meta tags in <head>
    - Working mobile hamburger menu with Alpine.js
    - Proper z-index hierarchy (navbar: 50, mobile menu: 40)
    - WCAG accessible with proper ARIA labels
    - WebP images with lazy loading

    ### CRITICAL: EMAILJS CONTACT FORM - USE EXACT CODE

    **IMPORTANT: For the contact section, use EXACTLY the code structure from BASE_HTML_TEMPLATE. DO NOT modify the form fields, IDs, JavaScript logic, or EmailJS implementation!**

    #### Required Contact Form Structure:
    1. **Form ID must be**: `emailjs-form`
    2. **Button ID must be**: `contact-btn`
    3. **Field names must be exactly**: `name`, `email`, `subject`, `message`, `to_email`
    4. **Message divs must be**: `success-message`, `error-message`, `error-text`

    #### EmailJS Integration Requirements:
    - Use `emailjs.sendForm(serviceID, templateID, form)` method exactly as in playground
    - Keep placeholders: `{{YOUR_EMAIL_JS_SERVICE_ID}}`, `{{YOUR_EMAIL_JS_TEMPLATE_ID}}`
    - Keep hidden field: `<input type="hidden" name="to_email" value="USER_EMAIL_PLACEHOLDER">`
    - Use vanilla JavaScript, NOT Alpine.js for contact form

    #### What you CAN customize:
    - Styling and colors to match website theme
    - Layout positioning and responsive design
    - Social media links
    - Label text and placeholders (but keep field names unchanged)

    #### What you CANNOT change:
    - Form field names and IDs
    - JavaScript event handling logic
    - EmailJS sendForm implementation
    - Placeholder replacement strings
    - Success/error message handling

    **RULE: If you see contact form code in BASE_HTML_TEMPLATE, copy it EXACTLY and only modify styling, never the structure or JavaScript logic.**

    This contact form structure is tested and working in EmailJS playground. Do not change it!

    Deliver only clean HTML code starting with <!DOCTYPE html>. No markdown, no explanations - just production-ready code that works perfectly across all devices and implements the approved design plan exactly for {user_theme} theme only.
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

            website_data = {
                'prompt': enhanced_prompt,
                'contact_email': design_plan.design_preferences.get('contact_email', ''),
                'primary_color': design_plan.design_preferences.get('primary_color', '#4B5EAA'),
                'secondary_color': design_plan.design_preferences.get('primary_color', '#4B5EAA'),
                'accent_color': design_plan.design_preferences.get('primary_color', '#4B5EAA'),
                'background_color': '#ffffff' if design_plan.design_preferences.get('theme') == 'light' else '#000000',
                'theme': design_plan.design_preferences.get('theme', 'light'),
                'heading_font': design_plan.design_preferences.get('heading_font', 'Playfair Display'),
                'body_font': design_plan.design_preferences.get('body_font', 'Inter'),
                'corner_radius': design_plan.design_preferences.get('corner_radius', 8)
            }
            
            website_serializer = WebsiteCreateSerializer(data=website_data, context={'request': request})
            website_serializer.is_valid(raise_exception=True)
            website = website_serializer.save()
            
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
                'message': 'Website successfully created from approved design plan'
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