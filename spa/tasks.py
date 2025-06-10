# apps/tasks.py (veya mevcut bir app içinde)
from celery import shared_task
import time

@shared_task
def test_task():
    """Basit test task'ı"""
    print("Test task çalışıyor...")
    time.sleep(2)
    print("Test task tamamlandı!")
    return "Test task başarılı"

@shared_task
def add(x, y):
    """Basit toplama task'ı"""
    return x + y

@shared_task
def send_email_task(email, subject, message):
    """Email gönderme task'ı (örnek)"""
    print(f"Email gönderiliyor: {email}")
    print(f"Konu: {subject}")
    print(f"Mesaj: {message}")
    # Burada gerçek email gönderme kodunuz olacak
    return f"Email {email} adresine gönderildi"