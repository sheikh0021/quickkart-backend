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
        return None

def send_order_status_notification(order, new_status):
    """Send notification based on order status change"""
    customer = order.customer

    if not customer.fcm_token:
        return None
    
    notifications = {
        'placed': {
            'title': 'QuickKart',
            'body': 'Your order is confirmed'
        },
        'packed': {
            'title': 'QuickKart',
            'body': 'Your order is packed'
        },
        'out_for_delivery': {
            'title': 'QuickKart',
            'body': 'Your order is out for delivery'
            },
        'delivered': {
            'title': 'QuickKart',
            'body': 'Your order has been delivered'
        }
        }
    if new_status in notifications:
        notifications = notifications[new_status]
        data = {
            'order_id': str(order.id),
            'order_number': order.order_number,
            'status': new_status
        }

        return send_push_notification(
            customer.fcm_token,
            notifications['title'],
            notifications['body'],
            data
        )
    return None
    