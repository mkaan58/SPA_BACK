#core/spa/models.py
from django.db import models
from users.models import User

class Website(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='websites')
    title = models.CharField(max_length=255)
    prompt = models.TextField()
    html_content = models.TextField()
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