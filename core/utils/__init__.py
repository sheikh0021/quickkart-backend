import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
import os

def initialize_firebase():
    """Initialize Firebase Admin SDK if not already initialized"""
    if not firebase_admin._apps:
        cred_path = os.path.join(settings.BASE_DIR, 'firebase-service-account.json')

        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            firebase_admin.initialize_app()

def send_push_notification(token, title, body, data=None):
    """Send push notification to a specific FCM token"""
    try:
        initialize_firebase()
        message= messaging.Message(
            notification = messaging.Notification(
                title=title,
                body=body,
            ),
            token=token,
            data=data or {}
        )
        response = messaging.send(message)
        return response 
    except Exception as e:
        print(f"Error sending push notification: {e}")

def send_order_status_notification(order, new_status):
    """Send notification based on order status change"""
    customer = order.customer

    if not customer.fcm_token:
        print(f"No FCM token for customer {customer.username}")
        return
    
    notifications = {
        'placed': {
            'title': f'New Order #{order.order_number}',
            'body': f'Order from {order.store.name} - ₹{order.total_amount}'
        },
        'confirmed': {
            'title': f'Order Confirmed #{order.order_number}',
            'body': 'Your Order has been confirmed and is being prepared'
        },
        'packed': {
            'title': f'Order Packed #{order.order_number}',
            'body': 'Your order is packed and ready for delivery'
        },
        'out_for_delivery': {
            'title': f'Out for delivery #{order.order_number}',
            'body': 'Your order is out for delivery'
            },
        'delivered': {
            'title': f'Order Delivered #{order.order_number}',
            'body': 'Your order has been delivered'
        }
        }
    if new_status in notifications:
        notification_data = notifications[new_status]

        # Send notification to customer for all status updates
        send_push_notification(
            customer.fcm_token,
            notification_data['title'],
            notification_data['body'],
            data={
                'order_id': str(order.id),
                'status': new_status
            }
        )

        # Send notification to admin for all status updates
        send_admin_notification(
            title=f'Order #{order.order_number} - {new_status.replace("_", " ").title()}',
            body=f'Customer: {customer.get_full_name()} - ₹{order.total_amount}',
            data={'order_id':str(order.id),
                  'status':new_status,
                  'type':'status_update'}
        )

def send_admin_notification(title, body, data=None):
    """Send notification to admin devices"""
    initialize_firebase()
    try:
        from apps.users.models import User
        admin_users = User.objects.filter(
            user_type='admin',
            fcm_token__isnull=False
        )

        if not admin_users:
            print("No admin users with FCM tokens found")
            print(f"Total admin users: {User.objects.filter(user_type='admin').count()}")
            print(f"Admin users without FCM tokens: {list(User.objects.filter(user_type='admin', fcm_token__isnull=True).values_list('username', flat=True))}")
            return

        success_count = 0
        for admin in admin_users:
            try:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body
                    ),
                    token=admin.fcm_token,
                    data=data or {}
                )

                response = messaging.send(message)
                success_count += 1
                print(f"Admin notification sent to {admin.username}: {response}")
            except Exception as e:
                print(f"Failed to send notification to {admin.username}: {e}")

        print(f"Admin notification sent to: {success_count} devices")
        return success_count
    except Exception as e:
        print(f"Error sending admin notification: {e}")

def send_chat_message_fcm(recipient_user, room, message):
    """Send FCM data message for new chat message. Recipient must have fcm_token."""
    try:
        if not getattr(recipient_user, 'fcm_token', None) or not recipient_user.fcm_token:
            print(f"No FCM token for {recipient_user.username}, skipping chat FCM")
            return
        initialize_firebase()
        from firebase_admin import messaging
        data = {
            'type': 'chat_message',
            'room_id': str(room.id),
            'id': str(message.id),
            'sender_id': str(message.sender.id),
            'sender_name': message.sender.username,
            'sender_type': message.sender.user_type,
            'message': message.message,
            'is_read': 'false',
            'created_at': message.created_at.isoformat(),
        }
        msg = messaging.Message(
            data=data,
            token=recipient_user.fcm_token,
        )
        messaging.send(msg)
    except Exception as e:
        print(f"Error sending chat FCM: {e}")


def send_delivery_notification(order, notification_type):
    """Send notification to assigned delivery partner"""
    initialize_firebase()
    try:
        assignment = order.delivery_assignment
        if not assignment:
            print(f"No delivery assignment found for order {order.id}")
            return
        
        delivery_partner = assignment.delivery_partner
        if not delivery_partner.fcm_token:
            print(f"No FCM token for delivery partner {delivery_partner.username}")
            return
        
        notifications = {
            'assigned': {
                'title': f'New Delivery Assignment #{order.order_number}',
                'body': f'Pickup from {order.store.name} - ₹{order.total_amount}'
            },
            'status_update': {
                'title': f'Order #{order.order_number} Status Update',
                'body': f'Order status changed to {order.status.replace("_", " ")}'
            }
        }
        if notification_type in notifications:
            notification_data = notifications[notification_type]

            send_push_notification(
                delivery_partner.fcm_token,
                notification_data['title'],
                notification_data['body'],
                data={
                    'order_id': str(order.id),
                    'type': notification_type,
                    'status': order.status
                }
            )
    except Exception as e: 
        print(f"Error sending delivery notification: {e}")