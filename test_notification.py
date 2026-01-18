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

from core.utils import send_admin_notification

def test_admin_notification():
    print("Testing admin notification...")

    try:
        result = send_admin_notification(
            title="Test Notification",
            body="This is a test notification to admin",
            data={"test": "true", "type": "test"}
        )
        print(f"✅ Admin notification test completed. Result: {result}")
    except Exception as e:
        print(f"❌ Admin notification test failed: {e}")

if __name__ == "__main__":
    test_admin_notification()