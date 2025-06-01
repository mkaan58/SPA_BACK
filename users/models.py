# users/models.py
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from .managers import CustomUserManager

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    surname = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    # Fields for email verification
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=255, blank=True, null=True)
    email_verification_token_created = models.DateTimeField(blank=True, null=True)
    social_provider = models.CharField(max_length=30, blank=True, null=True)
    
    # Fields for password reset
    password_reset_token = models.CharField(max_length=255, blank=True, null=True)
    password_reset_token_created = models.DateTimeField(blank=True, null=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def get_full_name(self):
        if self.name and self.surname:
            return f"{self.name} {self.surname}"
        return self.email
    
    def get_short_name(self):
        return self.name or self.email.split('@')[0]
        # Sosyal giriş bağlantısı olup olmadığını kontrol eden helper fonksiyon
    def has_social_login(self):
        return bool(self.social_provider)
    
    # Hem şifre hem de sosyal bağlantı kontrol
    def has_login_methods(self):
        return self.has_usable_password() or self.has_social_login()