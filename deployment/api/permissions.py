# deployment/api/permissions.py
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Sadece sahipler objeyi düzenleyebilir.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions herkes için
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions sadece sahip için
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'website'):
            return obj.website.user == request.user
        
        return False
