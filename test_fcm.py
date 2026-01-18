#!/usr/bin/env python3
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent / 'quickkart-backend' / 'quickkart-backend'
sys.path.append(str(BASE_DIR))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Test FCM functionality
from core.utils import initialize_firebase, send_push_notification
import firebase_admin
from firebase_admin import messaging

def test_fcm():
    try:
        print("Testing Firebase initialization...")
        initialize_firebase()
        print("✅ Firebase initialized successfully")

        # Check if apps are initialized
        if firebase_admin._apps:
            print("✅ Firebase app is initialized")
        else:
            print("❌ Firebase app is not initialized")
            return

        # Try to send a test notification (you'll need a valid FCM token)
        test_token = "test_token_here"  # Replace with actual token for testing

        if test_token != "test_token_here":
            print("Testing notification send...")
            try:
                response = send_push_notification(
                    test_token,
                    "Test Notification",
                    "This is a test notification from QuickKart"
                )
                print(f"✅ Test notification sent successfully: {response}")
            except Exception as e:
                print(f"❌ Failed to send test notification: {e}")
        else:
            print("⚠️  Skipping notification test (no test token provided)")

    except Exception as e:
        print(f"❌ FCM test failed: {e}")

if __name__ == "__main__":
    test_fcm()