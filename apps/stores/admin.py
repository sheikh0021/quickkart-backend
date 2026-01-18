from django.contrib import admin
from .models import Store

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone_number', 'is_active', 'delivery_radius')
    list_filter = ('is_active',)
    search_fields = ('name', 'address')