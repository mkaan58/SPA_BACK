# core/settings/prod.py
from .base import *
import dj_database_url
import os

DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database - Sadece bir kez tanımla
DATABASES = {
    'default': dj_database_url.parse(
        os.environ.get('DATABASE_URL', 
        'postgresql://spa_ozqv_user:ylYFYpqwh9bbFTqOh5FjBVkAX2fB5KXi@dpg-d144tsu3jp1c73d9dcpg-a.oregon-postgres.render.com/spa_ozqv')
    )
}

# HTTPS settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CORS settings for production
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')

# Frontend URL for production
FRONTEND_URL = os.environ.get('FRONTEND_URL')

# Celery ayarları
CELERY_BROKER_URL = os.environ.get('REDIS_URL')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Static files
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# API Keys
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your_default_gemini_api_key')
YOUR_EMAIL_JS_PUBLIC_KEY = os.environ.get('EMAIL_JS_PUBLIC_KEY')
YOUR_EMAIL_JS_PRIVATE_KEY = os.environ.get('EMAIL_JS_PRIVATE_KEY')
YOUR_EMAIL_JS_TEMPLATE_ID = os.environ.get('EMAIL_JS_TEMPLATE_ID')
YOUR_EMAIL_JS_SERVICE_ID = os.environ.get('EMAIL_JS_SERVICE_ID')

# GitHub Configuration
GITHUB_ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN', 'your_github_token_here')

# Vercel Configuration  
VERCEL_ACCESS_TOKEN = os.getenv('VERCEL_ACCESS_TOKEN', 'your_vercel_token_here')

# UNSPLASH Configuration
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY', 'your_unsplash_access_key_here')