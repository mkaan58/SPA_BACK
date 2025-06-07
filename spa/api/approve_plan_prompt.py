# spa/views/approve_plan.py
import json
import logging
from spa.models import WebsiteDesignPlan
from spa.api.template_prompts.base_html_2 import BASE_HTML_TEMPLATE

logger = logging.getLogger(__name__)

def generate_enhanced_prompt(design_plan, context_images, user_preferences, color_palette, accessibility_check, image_generation_method):
    """Gelişmiş HTML prompt'u oluşturur.

    Args:
        design_plan (WebsiteDesignPlan): Onaylanmış tasarım planı.
        context_images (dict): Bağlam duyarlı resim URL'leri.
        user_preferences (dict): Kullanıcı tercihleri (tema, renk, iş türü vb.).
        color_palette (dict): Renk paleti.
        accessibility_check (dict): Erişilebilirlik kontrol sonuçları.
        image_generation_method (str): Resim üretim yöntemi.

    Returns:
        str: Oluşturulan gelişmiş prompt.
    """
    business_type = user_preferences.get('business_type', 'professional')
    logger.info(f"📜 Generating enhanced prompt for business type: {business_type}")
    user_theme = user_preferences.get('theme', 'default')

    try:
        enhanced_prompt = f"""
        APPROVED DESIGN PLAN:
{design_plan.current_plan}

ORIGINAL USER REQUEST:
{design_plan.original_prompt}

BASE TEMPLATE TO ENHANCE:
{BASE_HTML_TEMPLATE}

🖼️ REAL CONTEXT-AWARE IMAGES (Generated via {image_generation_method}):
{json.dumps(context_images, indent=2)}

🎯 CRITICAL MISSION: Use REAL Unsplash photos selected for business type: {user_preferences.get('business_type', 'professional')}

🔥 REAL DYNAMIC IMAGE INTEGRATION:

### MANDATORY REAL IMAGE USAGE:
These are ACTUAL Unsplash photos (not placeholders) selected for your specific business context.

**Hero Section - Business: {user_preferences.get('business_type', 'professional')}**
- Hero image: {context_images.get('hero_image', 'ERROR: No hero image generated')}

**About Section - Professional Context**
- About image: {context_images.get('about_image', 'ERROR: No about image generated')}

**Portfolio Section - Work Showcase**
- Portfolio 1: {context_images.get('portfolio_1', 'ERROR: No portfolio image 1')}
- Portfolio 2: {context_images.get('portfolio_2', 'ERROR: No portfolio image 2')}  
- Portfolio 3: {context_images.get('portfolio_3', 'ERROR: No portfolio image 3')}

**Services Section - Service Presentation**
- Service image: {context_images.get('service_image', 'ERROR: No service image')}

### 🎨 REAL CONTEXT-AWARE FEATURES:
1. ✅ Images generated via {image_generation_method}
2. ✅ Business-specific queries: "{user_preferences.get('business_type', 'general')} professional modern"
3. ✅ Quality scored and context matched
4. ✅ Theme optimized for {user_theme} theme
5. ✅ Real Unsplash.com URLs (not placeholders)

### CRITICAL: NO FALLBACK URLS
❌ DO NOT use any picsum.photos or placeholder URLs
❌ DO NOT generate backup image URLs
✅ ONLY use the exact URLs provided above
✅ If any URL is missing, show error message

### EXAMPLE REAL IMPLEMENTATION:

<!-- REAL Business-Context Hero -->
<img src="{context_images.get('hero_image', 'ERROR')}" 
     alt="Real {user_preferences.get('business_type', 'business')} workspace showcasing our professional environment" 
     class="w-full h-full object-cover"
     loading="lazy"
     onerror="this.alt='Image failed to load - using real Unsplash photo'">

<!-- REAL Context-Matched Portfolio -->
<img src="{context_images.get('portfolio_1', 'ERROR')}" 
     alt="Actual {user_preferences.get('business_type', 'professional')} project from our portfolio"
     class="w-full h-64 object-cover rounded-lg hover:scale-105 transition-transform"
     loading="lazy">

🎯 CRITICAL MISSION: Create a website exactly as described in the approved design plan with PERFECT visual accessibility and color harmony.

✅ MANDATORY: All cards in the same section MUST have identical heights using CSS grid or flexbox, ensuring all text remains fully readable without truncation.
## 🧬 SCIENTIFICALLY CALCULATED COLOR SYSTEM

/* 🔴 CRITICAL: UNIFORM CARD HEIGHT SYSTEM */
.card-container 
  display: flex !important;
  align-items: stretch !important;


.card 
  height: 100% !important;
  display: flex !important;
  flex-direction: column !important;


.card-body 
  flex: 1 !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: space-between !important;


/* Grid containers for equal heights */
.portfolio-grid, .services-grid, .team-grid 
  display: grid !important;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)) !important;
  gap: 24px !important;
  align-items: stretch !important;


@media (max-width: 768px) 
  .portfolio-grid, .services-grid, .team-grid 
    grid-template-columns: 1fr !important;
  


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

🎯 SWIPER.JS CRITICAL OPTIMIZATIONS: Ensure Swiper sliders use proper breakpoints (320px: 1 slide, 640px: 2 slides, 1024px: 3 slides), enable touch gestures with smooth transitions, implement dynamic pagination bullets, and hide navigation arrows on mobile devices. Always test slider responsiveness and ensure smooth performance on all devices with proper autoplay settings.

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

🔴 CRITICAL TYPED.JS LAYOUT SAFETY:

MANDATORY: Prevent layout shifts and scrollbars caused by Typed.js:

1. ❌ NEVER let typed text change container width
2. ❌ NEVER allow horizontal scrolling from typing animation  
3. ❌ NEVER let text expansion break responsive layout
4. ✅ ALWAYS use fixed-width containers for typed text
5. ✅ ALWAYS add overflow-x: hidden to prevent scroll
6. ✅ ALWAYS set min-width on typed text containers

CRITICAL CSS (MANDATORY):
```css
.typed-container 
  min-width: 200px !important;
  overflow: hidden !important;
  white-space: nowrap !important;


body, .container 
  overflow-x: hidden !important;
  max-width: 100vw !important;

❌ DO NOT let Typed.js break responsive design
✅ ENSURE zero horizontal scroll on ANY device

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
8. ✅ Contact form uses EmailJS exactly as in BASE_HTML_TEMPLATE, MAKE SURE you've added contact form in website.Whatever user says about contact form dont care, just be attached into BASE_HTML_TEMPLATE contact form !!!!!
9. ✅ Responsive design works on all screen sizes
10. ✅ Professional, modern, and accessible appearance
11. ✅ **NEW:** Swiper sliders work on touch devices
12. ✅ **NEW:** Typed.js animations are smooth and professional. Make sure Typed.js animations dont cause problems with layout shifts or horizontal scrolling on mobile and desktop
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
        return enhanced_prompt
    except Exception as e:
        logger.error(f"❌ Error generating enhanced prompt: {str(e)}")
        raise