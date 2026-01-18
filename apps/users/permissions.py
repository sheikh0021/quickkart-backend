from rest_framework.permissions import  BasePermission

class IsCustomer(BasePermission):
    """Allow access only to customers"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'customer'

class IsDeliveryPartner(BasePermission):
    """Allow access only to delivery partners"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'delivery_partner'

class IsAdmin(BasePermission):
    """Allow access only to admins"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'admin'

class IsCustomerOrDeliveryPartner(BasePermission):
    """Allow access to customers and delivery partners"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.user_type in ['customer', 'delivery_partner']
        )
