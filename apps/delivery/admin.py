from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from apps.orders.models import Order
from .models import DeliveryAssignment, LocationUpdate

User = get_user_model()

@admin.register(DeliveryAssignment)
class DeliveryAssignmentAdmin(admin.ModelAdmin):
    list_display = ('order', 'delivery_partner', 'assigned_at', 'picked_up_at', 'delivered_at', 'status')
    list_filter = ('assigned_at', 'picked_up_at', 'delivered_at', 'delivery_partner')
    search_fields = ('order__order_number', 'delivery_partner__username')
    # Removed raw_id_fields to show proper dropdowns

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "delivery_partner":
            # Only show users with delivery_partner user_type
            kwargs["queryset"] = User.objects.filter(user_type='delivery_partner')
        elif db_field.name == "order":
            # Only show orders that don't have delivery assignments yet
            kwargs["queryset"] = Order.objects.filter(delivery_assignment__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    actions = ['marked_picked_up', 'marked_delivered']

    def status(self, obj):
        if not obj or not obj.pk:
            return "-"
        if obj.delivered_at:
            return mark_safe('<span style="color: green;">Delivered</span>')
        elif obj.picked_up_at:
            return mark_safe('<span style="color: blue;">Picked Up</span>')
        else:
            return mark_safe('<span style="color: orange;">Assigned</span>')
    status.short_description = "Status"
    
    def marked_picked_up(self, request, queryset):
        from django.utils import timezone
        queryset.filter(picked_up_at__isnull=True).update(picked_up_at=timezone.now())
        self.message_user(request, f"{queryset.count()} deliveries marked as picked up")
    marked_picked_up.short_description = "Mark selected as picked up"
    
    def marked_delivered(self, request, queryset):
        from django.utils import timezone
        queryset.filter(delivered_at__isnull=True).update(delivered_at=timezone.now())
        for assignment in queryset:
            assignment.order.status = 'delivered'
            assignment.order.save()
        self.message_user(request, f"{queryset.count()} deliveries marked as delivered")
    marked_delivered.short_description = "Mark selected as delivered"

@admin.register(LocationUpdate)
class LocationUpdateAdmin(admin.ModelAdmin):
    list_display = ('delivery_partner', 'order', 'latitude', 'longitude', 'timestamp')
    list_filter = ('timestamp', 'delivery_partner')
    search_fields = ('order__order_number', 'delivery_partner__username')

    actions = ['view_on_map']

    def view_on_map(self, request, queryset):
        if queryset.exists():
            location = queryset.first()
            map_url = f"https://www.google.com/maps?q={location.latitude},{location.longitude}"
            self.message_user(
                request,
                format_html(f'View location on <a href="{map_url}" target="_blank">Open Map</a>.')
            )
    view_on_map.short_description = "View selected location on map"