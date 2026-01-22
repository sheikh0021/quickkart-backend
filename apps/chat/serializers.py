from rest_framework import serializers
from .models import ChatRoom, ChatMessage
from apps.users.models import User

class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    sender_id = serializers.IntegerField(source='sender.id', read_only=True)
    sender_type = serializers.CharField(source='sender.user_type', read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'room', 'sender', 'sender_name', 'sender_id', 'sender_type', 
                  'message', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at', 'is_read']

class ChatRoomSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    delivery_partner_name = serializers.CharField(source='delivery_partner.username', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    unread_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'order', 'order_number', 'customer', 'customer_name', 
                  'delivery_partner', 'delivery_partner_name', 'is_active', 
                  'created_at', 'updated_at', 'unread_count', 'last_message']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_unread_count(self, obj):
        """Get unread message count for the current user"""
        request = self.context.get('request')
        if request and request.user:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0

    def get_last_message(self, obj):
        """Get the last message in the room"""
        last_msg = obj.messages.last()
        if last_msg:
            return ChatMessageSerializer(last_msg).data
        return None
