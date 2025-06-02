# utils/color_utils.py
import colorsys
import math

class ColorHarmonySystem:
    """Otomatik renk harmonisi ve kontrast kontrolü sistemi"""
    
    @staticmethod
    def hex_to_rgb(hex_color):
        """Hex rengi RGB'ye çevir"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def rgb_to_hex(rgb):
        """RGB'yi hex'e çevir"""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    @staticmethod
    def calculate_luminance(rgb):
        """Rengin luminance değerini hesapla (WCAG standardı)"""
        def normalize(c):
            c = c / 255.0
            return c / 12.92 if c <= 0.03928 else pow((c + 0.055) / 1.055, 2.4)
        
        r, g, b = [normalize(c) for c in rgb]
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    @staticmethod
    def contrast_ratio(color1_rgb, color2_rgb):
        """İki renk arasındaki kontrast oranını hesapla"""
        lum1 = ColorHarmonySystem.calculate_luminance(color1_rgb)
        lum2 = ColorHarmonySystem.calculate_luminance(color2_rgb)
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        return (lighter + 0.05) / (darker + 0.05)
    
    @staticmethod
    def adjust_brightness(rgb, factor):
        """Rengin parlaklığını ayarla (factor: -1 ile 1 arası)"""
        h, l, s = colorsys.rgb_to_hls(rgb[0]/255, rgb[1]/255, rgb[2]/255)
        l = max(0, min(1, l + factor))
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return (int(r * 255), int(g * 255), int(b * 255))
    
    @staticmethod
    def generate_accessible_colors(primary_hex, theme='light'):
        """Primary renge göre erişilebilir renk paleti oluştur"""
        primary_rgb = ColorHarmonySystem.hex_to_rgb(primary_hex)
        
        # Tema bazlı background ve text renkleri
        if theme == 'light':
            bg_rgb = (255, 255, 255)  # Beyaz
            text_rgb = (17, 24, 39)   # Koyu gri
            card_bg_rgb = (249, 250, 251)  # Açık gri
        else:
            bg_rgb = (15, 23, 42)     # Koyu lacivert
            text_rgb = (248, 250, 252) # Açık gri
            card_bg_rgb = (30, 41, 59) # Orta koyu gri
        
        # Primary color ile background arasındaki kontrast kontrolü
        primary_bg_contrast = ColorHarmonySystem.contrast_ratio(primary_rgb, bg_rgb)
        
        # Eğer primary color yeterli kontrast sağlamıyorsa ayarla
        if primary_bg_contrast < 4.5:  # WCAG AA standardı
            if theme == 'light':
                # Light tema için primary'yi koyulaştır
                primary_rgb = ColorHarmonySystem.adjust_brightness(primary_rgb, -0.3)
            else:
                # Dark tema için primary'yi aydınlatla
                primary_rgb = ColorHarmonySystem.adjust_brightness(primary_rgb, 0.3)
        
        # Secondary ve accent renkleri oluştur
        h, l, s = colorsys.rgb_to_hls(primary_rgb[0]/255, primary_rgb[1]/255, primary_rgb[2]/255)
        
        # Secondary (analog renk)
        secondary_h = (h + 0.08) % 1.0  # 30 derece kaydır
        secondary_rgb = tuple(int(c * 255) for c in colorsys.hls_to_rgb(secondary_h, l, s))
        
        # Accent (komplementer renk)
        accent_h = (h + 0.5) % 1.0  # 180 derece kaydır
        accent_rgb = tuple(int(c * 255) for c in colorsys.hls_to_rgb(accent_h, l, s))
        
        # Hover states için renkler
        primary_hover_rgb = ColorHarmonySystem.adjust_brightness(primary_rgb, -0.1 if theme == 'light' else 0.1)
        secondary_hover_rgb = ColorHarmonySystem.adjust_brightness(secondary_rgb, -0.1 if theme == 'light' else 0.1)
        
        # Border renkleri
        if theme == 'light':
            border_rgb = (229, 231, 235)  # Açık gri
            border_hover_rgb = (209, 213, 219)  # Daha koyu gri
        else:
            border_rgb = (71, 85, 105)   # Koyu gri
            border_hover_rgb = (100, 116, 139)  # Daha açık gri
        
        return {
            'primary': ColorHarmonySystem.rgb_to_hex(primary_rgb),
            'secondary': ColorHarmonySystem.rgb_to_hex(secondary_rgb),
            'accent': ColorHarmonySystem.rgb_to_hex(accent_rgb),
            'background': ColorHarmonySystem.rgb_to_hex(bg_rgb),
            'card_background': ColorHarmonySystem.rgb_to_hex(card_bg_rgb),
            'text_primary': ColorHarmonySystem.rgb_to_hex(text_rgb),
            'text_secondary': ColorHarmonySystem.rgb_to_hex(ColorHarmonySystem.adjust_brightness(text_rgb, 0.2 if theme == 'light' else -0.2)),
            'text_muted': ColorHarmonySystem.rgb_to_hex(ColorHarmonySystem.adjust_brightness(text_rgb, 0.4 if theme == 'light' else -0.4)),
            'border': ColorHarmonySystem.rgb_to_hex(border_rgb),
            'border_hover': ColorHarmonySystem.rgb_to_hex(border_hover_rgb),
            'primary_hover': ColorHarmonySystem.rgb_to_hex(primary_hover_rgb),
            'secondary_hover': ColorHarmonySystem.rgb_to_hex(secondary_hover_rgb),
            'success': '#10b981',  # Yeşil
            'warning': '#f59e0b',  # Sarı
            'error': '#ef4444',    # Kırmızı
            'info': '#3b82f6'      # Mavi
        }
    
    @staticmethod
    def validate_accessibility(color_palette):
        """Renk paletinin erişilebilirlik standartlarını kontrol et"""
        issues = []
        
        # Ana kontrast kontrolleri
        bg_rgb = ColorHarmonySystem.hex_to_rgb(color_palette['background'])
        text_rgb = ColorHarmonySystem.hex_to_rgb(color_palette['text_primary'])
        primary_rgb = ColorHarmonySystem.hex_to_rgb(color_palette['primary'])
        
        # Text kontrast kontrolü
        text_contrast = ColorHarmonySystem.contrast_ratio(text_rgb, bg_rgb)
        if text_contrast < 7.0:  # AAA standardı
            issues.append(f"Text kontrast oranı düşük: {text_contrast:.2f} (minimum 7.0)")
        
        # Primary button kontrast kontrolü
        primary_contrast = ColorHarmonySystem.contrast_ratio(primary_rgb, bg_rgb)
        if primary_contrast < 4.5:  # AA standardı
            issues.append(f"Primary button kontrast oranı düşük: {primary_contrast:.2f} (minimum 4.5)")
        
        return {
            'is_accessible': len(issues) == 0,
            'issues': issues,
            'scores': {
                'text_contrast': text_contrast,
                'primary_contrast': primary_contrast
            }
        }

# ViewSet'te kullanım örneği
def enhance_design_preferences(design_prefs):
    """Design preferences'ı renk harmonisi ile güçlendir"""
    primary_color = design_prefs.get('primary_color', '#4B5EAA')
    theme = design_prefs.get('theme', 'light')
    
    # Otomatik renk paleti oluştur
    color_palette = ColorHarmonySystem.generate_accessible_colors(primary_color, theme)
    
    # Erişilebilirlik kontrolü
    accessibility_check = ColorHarmonySystem.validate_accessibility(color_palette)
    
    # Design preferences'ı güncelle
    enhanced_prefs = design_prefs.copy()
    enhanced_prefs.update({
        'color_palette': color_palette,
        'accessibility_validated': accessibility_check['is_accessible'],
        'accessibility_scores': accessibility_check['scores']
    })
    
    return enhanced_prefs, color_palette