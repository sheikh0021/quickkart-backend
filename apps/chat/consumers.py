import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, ChatMessage
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode
from django.conf import settings

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection"""
        self.room_id = None
        self.room_group_name = None
        self.user = None

        # Get token from query string
        query_string = self.scope.get('query_string', b'').decode()
        token = None
        if 'token=' in query_string:
            token = query_string.split('token=')[-1].split('&')[0]
        
        if not token:
            await self.close()
            return

        # Authenticate user
        try:
            self.user = await self.authenticate_user(token)
            if not self.user:
                await self.close()
                return
        except Exception as e:
            await self.close()
            return

        # Get room_id from URL
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Verify user has access to this room
        has_access = await self.verify_room_access(self.room_id, self.user)
        if not has_access:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send message history
        await self.send_message_history()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle message received from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'chat_message':
                message_text = data.get('message', '').strip()
                if message_text:
                    # Save message to database
                    message = await self.save_message(self.room_id, self.user.id, message_text)
                    
                    # Broadcast message to room group
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': {
                                'id': message['id'],
                                'sender_id': message['sender_id'],
                                'sender_name': message['sender_name'],
                                'sender_type': message['sender_type'],
                                'message': message['message'],
                                'is_read': message['is_read'],
                                'created_at': message['created_at']
                            }
                        }
                    )
            elif message_type == 'read_receipt':
                # Mark messages as read
                await self.mark_messages_as_read(self.room_id, self.user.id)
                
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'read_receipt',
                        'user_id': self.user.id,
                        'room_id': self.room_id
                    }
                )

        except json.JSONDecodeError:
            pass
        except Exception as e:
            print(f"Error in receive: {e}")

    async def chat_message(self, event):
        """Send message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))

    async def read_receipt(self, event):
        """Send read receipt to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'user_id': event['user_id'],
            'room_id': event['room_id']
        }))

    @database_sync_to_async
    def authenticate_user(self, token):
        """Authenticate user from JWT token"""
        try:
            UntypedToken(token)
            decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_data.get('user_id')
            return User.objects.get(id=user_id)
        except (InvalidToken, TokenError, User.DoesNotExist) as e:
            return None

    @database_sync_to_async
    def verify_room_access(self, room_id, user):
        """Verify user has access to this chat room"""
        try:
            room = ChatRoom.objects.get(id=room_id)
            return room.customer == user or room.delivery_partner == user
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, room_id, user_id, message_text):
        """Save message to database"""
        room = ChatRoom.objects.get(id=room_id)
        user = User.objects.get(id=user_id)
        
        message = ChatMessage.objects.create(
            room=room,
            sender=user,
            message=message_text
        )
        
        # Update room's updated_at
        room.save(update_fields=['updated_at'])
        
        return {
            'id': message.id,
            'sender_id': user.id,
            'sender_name': user.username,
            'sender_type': user.user_type,
            'message': message.message,
            'is_read': message.is_read,
            'created_at': message.created_at.isoformat()
        }

    @database_sync_to_async
    def mark_messages_as_read(self, room_id, user_id):
        """Mark all unread messages in room as read (except sender's own messages)"""
        room = ChatRoom.objects.get(id=room_id)
        user = User.objects.get(id=user_id)
        
        ChatMessage.objects.filter(
            room=room,
            is_read=False
        ).exclude(sender=user).update(is_read=True)

    async def send_message_history(self):
        """Send message history to newly connected user"""
        messages = await self.get_message_history(self.room_id)
        await self.send(text_data=json.dumps({
            'type': 'message_history',
            'messages': messages
        }))

    @database_sync_to_async
    def get_message_history(self, room_id):
        """Get message history for room"""
        room = ChatRoom.objects.get(id=room_id)
        messages = ChatMessage.objects.filter(room=room).order_by('created_at')[:50]
        
        return [
            {
                'id': msg.id,
                'sender_id': msg.sender.id,
                'sender_name': msg.sender.username,
                'sender_type': msg.sender.user_type,
                'message': msg.message,
                'is_read': msg.is_read,
                'created_at': msg.created_at.isoformat()
            }
            for msg in messages
        ]
