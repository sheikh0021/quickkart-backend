from django.contrib import admin
from .models import User, CustomerProfile, DeliveryPartnerProfile
from django.contrib.auth.admin import UserAdmin

@admin.register(User)
class CustomerUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'phone_number', 'is_verified')
    list_filter = ('user_type', 'is_verified')
    search_fields = ('username', 'email', 'phone_number')

admin.site.register(CustomerProfile)
admin.site.register(DeliveryPartnerProfile)

ADMIN_SITE_HEADER = "QuickKart Admin Panel"
ADMIN_SITE_TITLE = "QuickKart Administration"
ADMIN_INDEX_TITLE = "Welcome to QuickKart Admin"

admin.site.site_header = ADMIN_SITE_HEADER
admin.site.site_title = ADMIN_SITE_TITLE
admin.site.index_title = ADMIN_INDEX_TITLE
  