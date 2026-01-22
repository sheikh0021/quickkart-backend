from django.db import models
from apps.users.models import User
from apps.orders.models import Order
from django.utils import timezone

class ChatRoom(models.Model):
    """Represents a chat room between customer and delivery partner for an order"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='chat_room')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_chat_rooms')
    delivery_partner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery_chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'chat_rooms'
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat Room for Order {self.order.order_number}"

class ChatMessage(models.Model):
    """Individual messages in a chat room"""
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.username} in Room {self.room.id}"

    def mark_as_read(self):
        """Mark message as read"""
        self.is_read = True
        self.save(update_fields=['is_read'])
