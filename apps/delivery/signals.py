from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DeliveryAssignment
from apps.chat.models import ChatRoom

@receiver(post_save, sender=DeliveryAssignment)
def create_chat_room_on_assignment(sender, instance, created, **kwargs):
    """Automatically create chat room when delivery partner is assigned"""
    if created:
        # Check if chat room already exists
        if not hasattr(instance.order, 'chat_room'):
            ChatRoom.objects.create(
                order=instance.order,
                customer=instance.order.customer,
                delivery_partner=instance.delivery_partner
            )
