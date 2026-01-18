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

from apps.users.models import User

def check_customer_tokens():
    print("Checking customers and their FCM tokens...")

    customers = User.objects.filter(user_type='customer')
    print(f"Total customers: {customers.count()}")

    for customer in customers:
        print(f"Customer: {customer.username}")
        print(f"  - ID: {customer.id}")
        print(f"  - FCM Token: {customer.fcm_token}")
        print(f"  - Is active: {customer.is_active}")
        print()

if __name__ == "__main__":
    check_customer_tokens()