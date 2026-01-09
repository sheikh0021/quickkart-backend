from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import DeliveryAssignment, LocationUpdate

User = get_user_model()

@admin.register(DeliveryAssignment)
class DeliveryAssignmentAdmin(admin.ModelAdmin):
    list_display = ('delivery_partner', 'order', 'assigned_at', 'picked_up_at', 'delivered_at', 'status')
    list_filter = ('assigned_at', 'picked_up_at', 'delivered_at')
    search_fields = ('order__order_number', 'delivery_partner__username')
    list_editable = ('picked_up_at', 'delivered_at')

    actions = ['marked_picked_up', 'marked_delivered']

    def status(self, obj):
        if obj.delivered_at:
            return format_html('<span style="color: green;">Delivered</span>')
        elif obj.picked_up_at:
            return format_html('<span style="color: blue;">Picked Up</span>')
        else:
            return format_html('<span style="color: orange;">Assigned</span>')
        status.short_description = "Status"
    
    def mark_picked_up(self, request, queryset):
        from django.utils import timezone
        queryset.filter(picked_up_at__isnull=True).update(picked_up_at=timezone.now())
        self.message_user(request, f"{queryset.count()} deliveries marked as picked up")
    
    def mark_delivered(self, request, queryset):
        from django.utils import timezone
        queryset.filter(delivered_at__isnull=True).update(delivered_at=timezone.now())
        for assignment in queryset:
            assignment.order.status = 'delivered'
            assignment.order.save()
        self.message_user(request, f"{queryset.count()} deliveries marked as delivered")
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "delivery_partner":
            kwargs["queryset"] = User.objects.filter(user_type='delivery_partner')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(LocationUpdate)
class LocationUpdateAdmin(admin.ModelAdmin):
    list_display = ('delivery_partner', 'order', 'latitude', 'longtitude', 'timestamp')
    list_filter = ('timestamp', 'delivery_partner')
    search_fields = ('order__order_number', 'delivery_partner__username')

    actions = ['view_on_map']

    def view_on_map(self, request, queryset):
        if queryset.exists():
            location = queryset.first()
            map_url = f"https://www.google.com/maps?q={location.latitude},{location.longtitude}"
            self.message_user(
                request,
                format_html(f'View location on <a href="{map_url}" target="_blank">Open Map</a>.')
            )
    view_on_map.short_description = "View selected location on map"