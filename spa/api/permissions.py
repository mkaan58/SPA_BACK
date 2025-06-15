# spa/api/permissions.py
from rest_framework.permissions import BasePermission
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class CanCreateWebsite(BasePermission):
    """
    Kullanıcının website oluşturup oluşturamayacağını kontrol eder
    Plan limitlerini kontrol eder:
    - Free: 2 website
    - Basic: 5 website  
    - Premium: 20 website
    """
    
    def has_permission(self, request, view):
        # Kullanıcı oturum açmış mı kontrol et
        if not request.user.is_authenticated:
            return False
        
        # Kullanıcının mevcut subscription type'ını al
        subscription_type = getattr(request.user, 'subscription_type', 'free')
        
        # Plan limitlerini belirle
        plan_limits = {
            'free': 2,
            'basic': 5,
            'premium': 20
        }
        
        max_websites = plan_limits.get(subscription_type, 2)  # Default free
        
        # Kullanıcının şu anki website sayısını kontrol et
        current_website_count = request.user.websites.count()
        
        # Limit kontrolü
        if current_website_count >= max_websites:
            # Limit aşıldığında request'e bilgi ekle
            request.limit_exceeded = True
            request.limit_details = {
                'subscription_type': subscription_type,
                'current_count': current_website_count,
                'max_websites': max_websites,
                'remaining': 0
            }
            
            logger.warning(f"User {request.user.id} has exceeded website limit: {current_website_count}/{max_websites} ({subscription_type})")
            return False
        else:
            # Limit bilgilerini request'e ekle
            request.limit_details = {
                'subscription_type': subscription_type,
                'current_count': current_website_count,
                'max_websites': max_websites,
                'remaining': max_websites - current_website_count
            }
            
            logger.debug(f"User {request.user.id} website creation allowed: {current_website_count}/{max_websites} ({subscription_type})")
            return True

class CanAccessWebsite(BasePermission):
    """
    Kullanıcının belirli bir website'e erişip erişemeyeceğini kontrol eder
    Sadece kendi website'lerine erişebilir
    """
    
    def has_object_permission(self, request, view, obj):
        # Website'in sahibi mi kontrol et
        return obj.user == request.user

class CanUpgradeSubscription(BasePermission):
    """
    Kullanıcının abonelik yükseltmesi yapıp yapamayacağını kontrol eder
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        current_subscription = getattr(request.user, 'subscription_type', 'free')
        
        # Zaten premium ise yükseltme yapamaz
        if current_subscription == 'premium':
            request.upgrade_blocked = True
            request.upgrade_reason = "Already on premium plan"
            return False
        
        return True

# Helper function - View'larda kullanmak için
def get_user_plan_info(user):
    """
    Kullanıcının plan bilgilerini döndürür
    """
    subscription_type = getattr(user, 'subscription_type', 'free')
    
    plan_info = {
        'subscription_type': subscription_type,
        'is_free': subscription_type == 'free',
        'is_basic': subscription_type == 'basic', 
        'is_premium': subscription_type == 'premium',
        'limits': {
            'free': {'websites': 2},
            'basic': {'websites': 5},
            'premium': {'websites': 20}
        }[subscription_type],
        'current_usage': {
            'websites': user.websites.count()
        }
    }
    
    # Kalan hakları hesapla
    plan_info['remaining'] = {
        'websites': max(0, plan_info['limits']['websites'] - plan_info['current_usage']['websites'])
    }
    
    # Abonelik expiry bilgisi
    if hasattr(user, 'subscription_expiry') and user.subscription_expiry:
        plan_info['subscription_expiry'] = user.subscription_expiry
        plan_info['is_active'] = user.subscription_expiry > timezone.now()
    else:
        plan_info['subscription_expiry'] = None
        plan_info['is_active'] = subscription_type == 'free'  # Free için her zaman active
    
    return plan_info