from django.db import models
from apps.users.models import User

class Banner(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='banners/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Store(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    phone_number = models.CharField(max_length=15)
    image = models.ImageField(upload_to='stores/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    delivery_radius = models.IntegerField(default=5)
    minimum_order = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def __str__(self):
        return self.name