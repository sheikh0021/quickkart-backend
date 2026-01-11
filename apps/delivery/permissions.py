from rest_framework.permissions import BasePermission


class IsDeliveryPartner(BasePermission):
    """
    Allow access only to delivery partners
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, 'user_type')
            and request.user.user_type == 'delivery_partner'
        )