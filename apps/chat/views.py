from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, ChatMessageSerializer
from apps.orders.models import Order
from apps.delivery.models import DeliveryAssignment

class ChatRoomListView(generics.ListAPIView):
    """List all chat rooms for the authenticated user"""
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'customer':
            return ChatRoom.objects.filter(customer=user, is_active=True)
        elif user.user_type == 'delivery_partner':
            return ChatRoom.objects.filter(delivery_partner=user, is_active=True)
        return ChatRoom.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class ChatRoomDetailView(generics.RetrieveAPIView):
    """Get details of a specific chat room"""
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'customer':
            return ChatRoom.objects.filter(customer=user)
        elif user.user_type == 'delivery_partner':
            return ChatRoom.objects.filter(delivery_partner=user)
        return ChatRoom.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class ChatMessageListView(generics.ListAPIView):
    """List messages in a chat room"""
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        user = self.request.user
        
        # Verify user has access to this room
        try:
            room = ChatRoom.objects.get(id=room_id)
            if room.customer != user and room.delivery_partner != user:
                return ChatMessage.objects.none()
            return ChatMessage.objects.filter(room=room).order_by('created_at')
        except ChatRoom.DoesNotExist:
            return ChatMessage.objects.none()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_or_create_chat_room(request, order_id):
    """Get or create a chat room for an order"""
    try:
        order = Order.objects.get(id=order_id)
        
        # Verify user has access to this order
        if request.user.user_type == 'customer':
            if order.customer != request.user:
                return Response(
                    {'error': 'Access denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        elif request.user.user_type == 'delivery_partner':
            try:
                assignment = DeliveryAssignment.objects.get(order=order)
                if assignment.delivery_partner != request.user:
                    return Response(
                        {'error': 'Access denied'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except DeliveryAssignment.DoesNotExist:
                return Response(
                    {'error': 'Order not assigned to delivery partner'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            return Response(
                {'error': 'Invalid user type'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if chat room exists
        if hasattr(order, 'chat_room'):
            room = order.chat_room
        else:
            # Check if order has delivery assignment
            try:
                assignment = DeliveryAssignment.objects.get(order=order)
                # Create new chat room
                room = ChatRoom.objects.create(
                    order=order,
                    customer=order.customer,
                    delivery_partner=assignment.delivery_partner
                )
            except DeliveryAssignment.DoesNotExist:
                return Response(
                    {'error': 'Order not assigned to delivery partner yet'},
                    status=status.HTTP_404_NOT_FOUND
                )

        serializer = ChatRoomSerializer(room, context={'request': request})
        return Response(serializer.data)
    except Order.DoesNotExist:
        return Response(
            {'error': 'Order not found'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, room_id):
    """Send a chat message and notify recipient via FCM"""
    try:
        room = ChatRoom.objects.get(id=room_id)
        if room.customer != request.user and room.delivery_partner != request.user:
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        message_text = (request.data.get('message') or '').strip()
        if not message_text:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

        msg = ChatMessage.objects.create(room=room, sender=request.user, message=message_text)
        recipient = room.delivery_partner if request.user == room.customer else room.customer

        from core.utils import send_chat_message_fcm
        send_chat_message_fcm(recipient, room, msg)

        serializer = ChatMessageSerializer(msg)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except ChatRoom.DoesNotExist:
        return Response({'error': 'Chat room not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_messages_as_read(request, room_id):
    """Mark all unread messages in a room as read"""
    try:
        room = ChatRoom.objects.get(id=room_id)
        
        # Verify user has access to this room
        if room.customer != request.user and room.delivery_partner != request.user:
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Mark messages as read (except sender's own messages)
        ChatMessage.objects.filter(
            room=room,
            is_read=False
        ).exclude(sender=request.user).update(is_read=True)
        
        return Response({'message': 'Messages marked as read'})
    except ChatRoom.DoesNotExist:
        return Response(
            {'error': 'Chat room not found'},
            status=status.HTTP_404_NOT_FOUND
        )
