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

from core.utils import send_order_status_notification
from apps.orders.models import Order

def test_customer_notification():
    print("Testing customer notification...")

    try:
        # Get the first order for testing
        order = Order.objects.first()
        if not order:
            print("❌ No orders found for testing")
            return

        print(f"Testing with Order: {order.order_number}")
        print(f"Customer: {order.customer.username}")
        print(f"Customer FCM Token: {order.customer.fcm_token}")

        result = send_order_status_notification(order, 'placed')
        print(f"✅ Customer notification test completed.")

    except Exception as e:
        print(f"❌ Customer notification test failed: {e}")

if __name__ == "__main__":
    test_customer_notification()