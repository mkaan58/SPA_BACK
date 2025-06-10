
# core/settings/base.py
import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-ps=5nj4rj4dih4(cc8b34a)t7922-ea1!r8&8#x3fbk(-ihkg!')

DEBUG = True

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Add this
    
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'allauth',  # Add this
    'allauth.account',  # Add this
    'allauth.socialaccount',  # Add this
    'allauth.socialaccount.providers.google',  # Add this
    'django_extensions',
    
    # Local apps
    'users.apps.UsersConfig',
    'spa.apps.SpaConfig',
    'deployment.apps.DeploymentConfig',
    'celery',
    'django_redis',

]

# Add site ID
SITE_ID = 1
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
# Add authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Add social account settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
            'secret': os.environ.get('GOOGLE_CLIENT_SECRET', ''),
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'users.User'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),

    'DEFAULT_PAGINATION_CLASS': 'spa.api.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 3,

}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

# CORS settings
CORS_ALLOW_CREDENTIALS = True

# Frontend URL for email verification and password reset links
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')



LEMON_SQUEEZY_API_KEY = os.environ.get('LEMON_SQUEEZY_API_KEY')
LEMON_SQUEEZY_STORE_ID = os.environ.get('LEMON_SQUEEZY_STORE_ID')
LEMON_SQUEEZY_WEBHOOK_SECRET = os.environ.get('LEMON_SQUEEZY_WEBHOOK_SECRET')
LEMON_SQUEEZY_CHECKOUT_URL = os.environ.get('LEMON_SQUEEZY_CHECKOUT_URL')
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY', 'your_unsplash_access_key_here')

# import os

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
    
#     # Formatters - Log mesajlarının formatı
#     'formatters': {
#         'verbose': {
#             'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
#             'style': '{',
#         },
#         'simple': {
#             'format': '{levelname} {message}',
#             'style': '{',
#         },
#         'colored': {
#             'format': '\033[92m[{asctime}]\033[0m \033[94m{levelname}\033[0m \033[93m{name}\033[0m: {message}',
#             'style': '{',
#         },
#         'detailed': {
#             'format': '🔍 [{asctime}] {levelname:8} {name:30} {funcName:20} L{lineno:3d}: {message}',
#             'style': '{',
#             'datefmt': '%Y-%m-%d %H:%M:%S'
#         }
#     },
    
#     # Handlers - Log mesajlarının nereye gideceği
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#             'formatter': 'detailed',
#             'level': 'DEBUG',
#         },
#         'file': {
#             'class': 'logging.FileHandler',
#             'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
#             'formatter': 'verbose',
#             'level': 'DEBUG',
#         },
#         'error_file': {
#             'class': 'logging.FileHandler',
#             'filename': os.path.join(BASE_DIR, 'logs', 'errors.log'),
#             'formatter': 'verbose',
#             'level': 'ERROR',
#         },
#         'api_file': {
#             'class': 'logging.FileHandler',
#             'filename': os.path.join(BASE_DIR, 'logs', 'api.log'),
#             'formatter': 'detailed',
#             'level': 'DEBUG',
#         }
#     },
    
#     # Loggers - Hangi modülün logları nasıl işlenecek
#     'loggers': {
#         # Django'nun kendi logları
#         'django': {
#             'handlers': ['console', 'file'],
#             'level': 'INFO',
#             'propagate': False,
#         },
        
#         # Django istekleri (her HTTP request)
#         'django.request': {
#             'handlers': ['console', 'error_file'],
#             'level': 'DEBUG',
#             'propagate': False,
#         },
        
#         # Database sorguları
#         'django.db.backends': {
#             'handlers': ['console'],
#             'level': 'DEBUG',
#             'propagate': False,
#         },
        
#         # SPA services
#         'spa.services': {
#             'handlers': ['console', 'api_file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
        
#         # SPA API views
#         'spa.api.views': {
#             'handlers': ['console', 'api_file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
        
#         # SPA models
#         'spa.models': {
#             'handlers': ['console', 'api_file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
        
#         # Tüm SPA uygulaması
#         'spa': {
#             'handlers': ['console', 'api_file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
        
#         # Root logger - Tüm diğer loglar
#         '': {
#             'handlers': ['console', 'file'],
#             'level': 'INFO',
#         },
#     },
    
#     # Root logger configuration
#     'root': {
#         'level': 'DEBUG',
#         'handlers': ['console'],
#     }
# }

# # Logs klasörünü oluştur
# LOGS_DIR = os.path.join(BASE_DIR, 'logs')
# if not os.path.exists(LOGS_DIR):
#     os.makedirs(LOGS_DIR)

# # Debug mode'da daha detaylı loglar
# if DEBUG:
#     # Console'da renklendirme
#     LOGGING['handlers']['console']['formatter'] = 'colored'
    
#     # Tüm SQL sorgularını göster
#     LOGGING['loggers']['django.db.backends']['level'] = 'DEBUG'
    
#     # Django debug toolbar logları
#     LOGGING['loggers']['django.template'] = {
#         'handlers': ['console'],
#         'level': 'INFO',
#         'propagate': False,
#     }

# # Production'da log seviyelerini artır
# else:
#     LOGGING['handlers']['console']['level'] = 'WARNING'
#     LOGGING['loggers']['django']['level'] = 'WARNING'
#     LOGGING['loggers']['django.request']['level'] = 'ERROR'


# os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)
