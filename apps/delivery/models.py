from django.db import models
from apps.users.models import User, DeliveryPartnerProfile
from apps.orders.models import Order

class DeliveryAssignment(models.Model):
    delivery_partner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deliveries')
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery_assignment')
    assigned_at = models.DateTimeField(auto_now_add=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Delivery: {self.order.order_number} -> {self.delivery_partner.username}"
    
class LocationUpdate(models.Model):
    delivery_partner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='location_updates')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='location_updates')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Location: {self.delivery_partner.username} at {self.timestamp}"


class DeliveryEarnings(models.Model):
    delivery_partner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earnings')
    assignment = models.OneToOneField(DeliveryAssignment, on_delete=models.CASCADE, related_name='earnings')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-earned_at']

    def __str__(self):
        return f"Earnings: {self.delivery_partner.username} - ₹{self.amount}"

