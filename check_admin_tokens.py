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

def check_admin_tokens():
    print("Checking admin users and their FCM tokens...")

    admin_users = User.objects.filter(user_type='admin')
    print(f"Total admin users: {admin_users.count()}")

    for admin in admin_users:
        print(f"Admin: {admin.username}")
        print(f"  - ID: {admin.id}")
        print(f"  - FCM Token: {admin.fcm_token}")
        print(f"  - Is active: {admin.is_active}")
        print()

    if not admin_users.exists():
        print("No admin users found. Creating a test admin user...")

        # Create a test admin user
        test_admin = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='admin123',
            user_type='admin',
            first_name='Test',
            last_name='Admin'
        )
        print(f"Created test admin user: {test_admin.username}")

if __name__ == "__main__":
    check_admin_tokens()