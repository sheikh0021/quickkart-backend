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

def check_delivery_tokens():
    print("Checking delivery partners and their FCM tokens...")

    delivery_partners = User.objects.filter(user_type='delivery_partner')
    print(f"Total delivery partners: {delivery_partners.count()}")

    for partner in delivery_partners:
        print(f"Delivery Partner: {partner.username}")
        print(f"  - ID: {partner.id}")
        print(f"  - FCM Token: {partner.fcm_token}")
        print(f"  - Is active: {partner.is_active}")
        print()

    if not delivery_partners.exists():
        print("No delivery partners found.")

if __name__ == "__main__":
    check_delivery_tokens()