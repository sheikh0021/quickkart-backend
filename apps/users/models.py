from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('delivery_partner', 'Delivery Partner'),
        ('admin', 'Admin'),
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    phone_number = models.CharField(max_length=15, unique=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.get_user_type})"
    
class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    preferred_payment = models.CharField(max_length=20, default='cod')

    def __str__(self):
        return f"Customer: {self.user.username}"
    
class DeliveryPartnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='delivery_partner_profile')
    vehicle_number = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=20, choices=[
        ('bike', 'Bike'),
        ('scooter', 'Scooter'),
        ('car', 'Car'),
    ] )

    is_available = models.BooleanField(default=True)
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)

    def __str__(self):
        return f"Delivery Partner: {self.user.username}"
    
