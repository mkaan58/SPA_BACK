# core/urls.py
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.api.urls')),
    path('api/spa/', include('spa.api.urls')),  
    path('api/deployment/', include('deployment.api.urls')),
    path('api/payments/',include('payments.urls')),
]

