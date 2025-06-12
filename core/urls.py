# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.api.urls')),
    path('api/spa/', include('spa.api.urls')),  
    path('api/deployment/', include('deployment.api.urls')),
]

# Add static and media URLs for development
# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not settings.DEBUG: # DEBUG False iken çalışsın
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Genellikle statik dosyaları Whitenoise veya Nginx/Apache sunar, bu kısım zorunlu değil
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)