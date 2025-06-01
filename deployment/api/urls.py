# deployment/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeploymentViewSet, DeploymentSettingsViewSet

router = DefaultRouter()
router.register(r'deployments', DeploymentViewSet, basename='deployment')
router.register(r'settings', DeploymentSettingsViewSet, basename='deployment-settings')

urlpatterns = [
    path('', include(router.urls)),
]