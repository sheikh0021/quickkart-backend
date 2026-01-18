#!/usr/bin/env python3
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.utils import send_delivery_notification
from apps.orders.models import Order
from apps.users.models import User

def test_delivery_notification():
    print("Testing delivery partner notification...")

    try:
        # Get the first order and delivery partner for testing
        order = Order.objects.first()
        if not order:
            print("❌ No orders found for testing")
            return

        delivery_partner = User.objects.filter(user_type='delivery_partner').first()
        if not delivery_partner:
            print("❌ No delivery partners found for testing")
            return

        print(f"Testing with Order: {order.order_number}")
        print(f"Testing with Delivery Partner: {delivery_partner.username}")

        # Create a mock assignment for testing
        from apps.delivery.models import DeliveryAssignment
        assignment, created = DeliveryAssignment.objects.get_or_create(
            order=order,
            defaults={'delivery_partner': delivery_partner}
        )

        result = send_delivery_notification(order, 'assigned')
        print(f"✅ Delivery notification test completed. Result: {result}")

    except Exception as e:
        print(f"❌ Delivery notification test failed: {e}")

if __name__ == "__main__":
    test_delivery_notification()