# payments/urls.py
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('subscription/', views.SubscriptionDetailView.as_view(), name='subscription-detail'),
    path('history/', views.PaymentHistoryView.as_view(), name='payment-history'),
    path('webhook/lemon-squeezy/', views.lemon_squeezy_webhook, name='lemon-squeezy-webhook'),
]
