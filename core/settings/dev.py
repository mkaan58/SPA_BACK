# core/settings/dev.py
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS settings for development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_ALL_ORIGINS = False

# Frontend URL for development
FRONTEND_URL = 'http://localhost:3000'

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your_default_gemini_api_key')

# Celery settings for development
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'


YOUR_EMAIL_JS_PUBLIC_KEY = os.environ.get('EMAIL_JS_PUBLIC_KEY')
YOUR_EMAIL_JS_PRIVATE_KEY = os.environ.get('EMAIL_JS_PRIVATE_KEY')
YOUR_EMAIL_JS_TEMPLATE_ID = os.environ.get('EMAIL_JS_TEMPLATE_ID')
YOUR_EMAIL_JS_SERVICE_ID = os.environ.get('EMAIL_JS_SERVICE_ID')


# GitHub Configuration
GITHUB_ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN', 'your_github_token_here')
# GITHUB_ORGANIZATION = os.getenv('GITHUB_ORGANIZATION', 'your_github_org_here')

# Vercel Configuration  
VERCEL_ACCESS_TOKEN = os.getenv('VERCEL_ACCESS_TOKEN', 'your_vercel_token_here')

# UNSPLASH Configuration
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY', 'your_unsplash_access_key_here')
