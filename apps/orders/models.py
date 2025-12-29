from django.db import models
from apps.users.models import User, CustomerProfile
from apps.stores.models import Store

class Order(models.Model):
    STATUS_CHOICES = (
        ('placed', 'Placed'),
        ('confirmed', 'Confirmed'),
        ('packed', 'Packed'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),    
    )

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='placed')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_address = models.TextField()
    delivery_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_longtitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    payment_method = models.CharField(max_length=20, default='cod')
    payment_status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_number}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"