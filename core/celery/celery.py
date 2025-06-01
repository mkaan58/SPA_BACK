# core/celery/celery.py
import os
from celery import Celery

# Django ayarlarını Celery için varsayılan olarak ayarlayın
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.prod')

app = Celery('core')  # Projenizin adını buraya yazın

# Django ayarlarından yapılandırma
app.config_from_object('django.conf:settings', namespace='CELERY')

# Tüm projenizdeki görevleri otomatik keşfedin
app.autodiscover_tasks()
