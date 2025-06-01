# deployment/apps.py
from django.apps import AppConfig


class DeploymentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'deployment'
    
    def ready(self):
        import deployment.api.signals
