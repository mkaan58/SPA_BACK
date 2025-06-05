#core/spa/models.py
from django.db import models
from users.models import User

class Website(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='websites')
    title = models.CharField(max_length=255)
    prompt = models.TextField()
    html_content = models.TextField()
    custom_styles = models.JSONField(default=dict, blank=True)  # YENİ ALAN
    element_contents = models.JSONField(default=dict, blank=True)  # YENİ ALAN - text içerikleri için

    # Yeni alanlar
    primary_color = models.CharField(max_length=7, blank=True)  # #FFFFFF formatında
    secondary_color = models.CharField(max_length=7, blank=True)
    accent_color = models.CharField(max_length=7, blank=True)
    background_color = models.CharField(max_length=7, blank=True)
    theme = models.CharField(max_length=10, choices=[('light', 'Light'), ('dark', 'Dark')], default='light')
    heading_font = models.CharField(max_length=100, blank=True)
    body_font = models.CharField(max_length=100, blank=True)
    corner_radius = models.IntegerField(default=8)  # Piksel cinsinden
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    contact_email = models.EmailField(blank=True, null=True)  # Kullanıcı iletişim maili

    def apply_custom_styles_to_html(self):
        """Custom styles'ı HTML'e CSS olarak ekle"""
        if not self.custom_styles:
            return self.html_content
        
        # CSS oluştur
        css_rules = []
        for element_id, styles in self.custom_styles.items():
            style_declarations = []
            for prop, value in styles.items():
                style_declarations.append(f"{prop}: {value} !important")
            
            if style_declarations:
                css_rules.append(f"[data-element-id='{element_id}'] {{ {'; '.join(style_declarations)}; }}")
        
        if css_rules:
            custom_css = f"""
            <style data-custom-styles="true">
            /* Custom user styles - Auto generated */
            {chr(10).join(css_rules)}
            </style>
            """
            
            # Head'e ekle
            if '</head>' in self.html_content:
                return self.html_content.replace('</head>', f'{custom_css}</head>')
            else:
                return f"{custom_css}{self.html_content}"
        
        return self.html_content


    def apply_all_customizations_safe(self):
        """SAFE version - only for final rendering"""
        html_content = self.html_content
        
        # SADECE preview için CSS/JS ekle, orijinal HTML'i değiştirme
        if self.custom_styles:
            css_rules = []
            for element_id, styles in self.custom_styles.items():
                style_declarations = []
                for prop, value in styles.items():
                    style_declarations.append(f"{prop}: {value} !important")
                
                if style_declarations:
                    css_rules.append(f"[data-element-id='{element_id}'] {{ {'; '.join(style_declarations)}; }}")
            
            if css_rules:
                custom_css = f"""
                <style data-custom-styles="true">
                /* Custom user styles */
                {chr(10).join(css_rules)}
                </style>
                """
                
                if '</head>' in html_content:
                    html_content = html_content.replace('</head>', f'{custom_css}</head>')
                else:
                    html_content = f"{custom_css}{html_content}"
        
        return html_content

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class UploadedImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_images')
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='uploads/%Y/%m/%d/')
    title = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class WebsiteDesignPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='design_plans')
    original_prompt = models.TextField()
    current_plan = models.TextField()  # Markdown formatında tasarım planı
    feedback_history = models.JSONField(default=list)  # Kullanıcı feedback'lerinin geçmişi
    design_preferences = models.JSONField(default=dict)  # Renk, font vs. bilgileri
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Design Plan - {self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"