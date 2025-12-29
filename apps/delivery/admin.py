from django.contrib import admin
from .models import DeliveryAssignment, LocationUpdate

@admin.register(DeliveryAssignment)
class DeliveryAssignmentAdmin(admin.ModelAdmin):
    list_display = ('delivery_partner', 'order', 'assigned_at', 'delivered_at')
    list_filter = ('assigned_at', 'delivered_at')

@admin.register(LocationUpdate)
class LocationUpdateAdmin(admin.ModelAdmin):
    list_display = ('delivery_partner', 'order', 'timestamp')
    list_filter = ('timestamp',)