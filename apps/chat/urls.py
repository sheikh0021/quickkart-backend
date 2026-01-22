from django.urls import path
from . import views

urlpatterns = [
    path('rooms/', views.ChatRoomListView.as_view(), name='chat-room-list'),
    path('rooms/<int:pk>/', views.ChatRoomDetailView.as_view(), name='chat-room-detail'),
    path('rooms/<int:room_id>/messages/', views.ChatMessageListView.as_view(), name='chat-message-list'),
    path('rooms/<int:room_id>/messages/send/', views.send_message, name='send-message'),
    path('orders/<int:order_id>/room/', views.get_or_create_chat_room, name='get-or-create-chat-room'),
    path('rooms/<int:room_id>/mark-read/', views.mark_messages_as_read, name='mark-messages-read'),
]
