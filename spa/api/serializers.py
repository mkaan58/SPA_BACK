#core/spa/api/serializers.py
from rest_framework import serializers
from spa.models import Website, UploadedImage, WebsiteDesignPlan

# In serializers.py
class WebsiteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Website
        fields = [
            'id', 'title', 'prompt', 'html_content','contact_email',
            'primary_color', 'secondary_color', 'accent_color', 'background_color',
            'theme', 'heading_font', 'body_font', 'corner_radius',
            'created_at', 'updated_at', 'custom_styles', 'element_contents',
            'original_user_prompt', 'business_context','custom_domain','custom_domain_verified'  # YENİ ALANLAR EKLE
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    


class WebsiteCreateSerializer(serializers.ModelSerializer):
    contact_email = serializers.EmailField(required=False, allow_blank=True)
    primary_color = serializers.CharField(required=False, allow_blank=True)
    secondary_color = serializers.CharField(required=False, allow_blank=True)
    accent_color = serializers.CharField(required=False, allow_blank=True)
    background_color = serializers.CharField(required=False, allow_blank=True)
    theme = serializers.ChoiceField(choices=[('light', 'Light'), ('dark', 'Dark')], default='light')
    heading_font = serializers.CharField(required=False, allow_blank=True)
    body_font = serializers.CharField(required=False, allow_blank=True)
    corner_radius = serializers.IntegerField(default=8)

    class Meta:
        model = Website
        fields = [
            'prompt','contact_email',
            'primary_color', 'secondary_color', 'accent_color', 'background_color',
            'theme', 'heading_font', 'body_font', 'corner_radius',
            'original_user_prompt', 'business_context'  # YENİ ALANLAR EKLE
        ]

    def create(self, validated_data):
        prompt_text = validated_data['prompt']
        
        # YENİ: Original prompt'u kaydet
        original_prompt = validated_data.get('original_user_prompt', '')
        
        # Eğer original_user_prompt boşsa ve normal prompt enhanced değilse, onu original olarak kaydet
        if not original_prompt and not prompt_text.startswith(('APPROVED DESIGN PLAN:', '**APPROVED DESIGN PLAN:')):
            original_prompt = prompt_text
        
        # ✅ Enhanced prompt kontrolü (mevcut kod - değişiklik yok)
        if prompt_text.startswith(('APPROVED DESIGN PLAN:', '**APPROVED DESIGN PLAN:')):
            title = self._extract_title_from_enhanced_prompt(prompt_text)
        else:
            words = prompt_text.split()
            title = ' '.join(words[:5]) + '...' if len(words) > 5 else prompt_text

        return Website(
            user=self.context['request'].user,
            title=title,
            prompt=prompt_text,
            html_content='',
            original_user_prompt=original_prompt,  # YENİ ALAN
            business_context=validated_data.get('business_context', {}),  # YENİ ALAN
            contact_email=validated_data.get('contact_email', ''),
            primary_color=validated_data.get('primary_color', ''),
            secondary_color=validated_data.get('secondary_color', ''),
            accent_color=validated_data.get('accent_color', ''),
            background_color=validated_data.get('background_color', ''),
            theme=validated_data.get('theme', 'light'),
            heading_font=validated_data.get('heading_font', ''),
            body_font=validated_data.get('body_font', ''),
            corner_radius=validated_data.get('corner_radius', 8)
        )
    def _extract_title_from_enhanced_prompt(self, enhanced_prompt):
        """Enhanced prompt'tan anlamlı title çıkar"""
        try:
            # "ORIGINAL USER REQUEST:" kısmını bul
            if "ORIGINAL USER REQUEST:" in enhanced_prompt:
                lines = enhanced_prompt.split('\n')
                for i, line in enumerate(lines):
                    if "ORIGINAL USER REQUEST:" in line and i + 1 < len(lines):
                        original = lines[i + 1].strip()
                        if original and not original.startswith(('APPROVED', 'BASE', '🖼️', '🎯')):
                            words = original.split()
                            return ' '.join(words[:5]) + '...' if len(words) > 5 else original
            
            # Plan içinden business type çıkarmaya çalış
            business_indicators = {
                'restaurant': 'Restaurant Website',
                'portfolio': 'Portfolio Website', 
                'business': 'Business Website',
                'photography': 'Photography Portfolio',
                'consulting': 'Consulting Website',
                'shop': 'Shop Website',
                'blog': 'Blog Website'
            }
            
            prompt_lower = enhanced_prompt.lower()
            for keyword, title in business_indicators.items():
                if keyword in prompt_lower:
                    return title
                    
            # Fallback
            return "AI Generated Website"
        except:
            return "Generated Website"

class UploadedImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UploadedImage
        fields = ['id', 'title', 'image', 'image_url', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at', 'image_url']
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url') and request:
            return request.build_absolute_uri(obj.image.url)
        return None

class WebsiteDesignPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteDesignPlan
        fields = [
            'id', 'original_prompt', 'current_plan', 'feedback_history', 
            'design_preferences', 'is_approved', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class AnalyzePromptSerializer(serializers.Serializer):
    prompt = serializers.CharField()
    primary_color = serializers.CharField(required=False, allow_blank=True)
    contact_email = serializers.EmailField(required=False, allow_blank=True)  # ➕ EKLE
    theme = serializers.ChoiceField(choices=[('light', 'Light'), ('dark', 'Dark')], default='light')
    heading_font = serializers.CharField(required=False, allow_blank=True)
    body_font = serializers.CharField(required=False, allow_blank=True)
    corner_radius = serializers.IntegerField(default=8)

class UpdatePlanSerializer(serializers.Serializer):
    feedback = serializers.CharField()


# serializers.py - Yeni serializer ekle
class ElementStyleSerializer(serializers.Serializer):
    element_selector = serializers.CharField(max_length=100)
    property = serializers.CharField(max_length=50)
    value = serializers.CharField(max_length=200)
    element_id = serializers.CharField(max_length=100, required=False)



class AIStructuralEditSerializer(serializers.Serializer):
    """Serializer for AI structural edit requests"""
    ai_prompt = serializers.CharField(max_length=2000, help_text="AI edit instruction")
    selected_element = serializers.JSONField(required=False, help_text="Currently selected element context")
    
    def validate_ai_prompt(self, value):
        """Validate AI prompt"""
        if not value.strip():
            raise serializers.ValidationError("AI prompt cannot be empty")
        
        # Check for potentially harmful requests
        harmful_keywords = ['delete all', 'remove everything', 'format hard drive', 'rm -rf']
        if any(keyword in value.lower() for keyword in harmful_keywords):
            raise serializers.ValidationError("Request contains potentially harmful instructions")
        
        return value.strip()
