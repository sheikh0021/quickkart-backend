from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from django.utils import timezone
import csv
from .models import Order, OrderItem
from apps.delivery.models import DeliveryAssignment

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'quantity', 'unit_price', 'total_price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'store', 'status', 'total_amount', 'created_at', 'delivery_status')
    list_filter = ('status', 'created_at', 'store')
    search_fields = ('order_number', 'customer__username')
    list_editable = ('status',)
    inlines = [OrderItemInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('delivery_assignment')

    actions = ['assign_delivery_partner', 'mark_packed', 'mark_out_for_delivery', 'mark_delivered', 'export_selected_orders_csv', 'export_selected_orders_excel']

    def export_selected_orders_csv(self, request, queryset):
        """Export selected orders to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="orders_{timezone.now().date()}.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Order Number', 'Customer', 'Store', 'Status', 'Total Amount',
            'Delivery Address', 'Payment Method', 'Created At'
        ])

        for order in queryset:
            writer.writerow([
                order.order_number,
                order.customer.username,
                order.store.name,
                order.status,
                order.total_amount,
                order.delivery_address,
                order.payment_method,
                order.created_at.date()
            ])
        return response
    export_selected_orders_csv.short_description = "Export selected orders to CSV"

    def export_selected_orders_excel(self, request, queryset):
        """Export selected orders to Excel (simplified CSV for now)"""
        return self.export_selected_orders_csv(request, queryset)
    export_selected_orders_excel.short_description = "Export selected orders to Excel"

    def delivery_status(self, obj):
        """Show delivery assignment status"""
        try:
            assignment = obj.delivery_assignment
            if assignment.delivered_at:
                return "Delivered"
            elif assignment.picked_up_at:
                return "Out for Delivery"
            else:
                return "Assigned"
        except:
            return "Not Assigned"
    delivery_status.short_description = "Delivery Status"

    def assign_delivery_partner(self, request, queryset):
        """Action to assign delivery partner (opens popup or redirects to assignment page)"""
        selected_orders = list(queryset.values_list('id', flat=True))
        self.message_user(
            request,
            f"Selected {len(selected_orders)} orders for delivery assignment. "
            "Use the Delivery Assignment section to assign partners."
        )
    assign_delivery_partner.short_description = "Assign delivery partner to selected orders"
    
    def mark_packed(self, request, queryset):
        queryset.filter(status='confirmed').update(status='packed')
        self.message_user(request, f"{queryset.count()} orders marked as packed.")
    
    def mark_out_for_delivery(self, request, queryset):
        queryset.filter(status='packed').update(status='out_for_delivery')
        self.message_user(request, f"{queryset.count()} orders marked as out for delivery.")
    
    def mark_delivered(self, request, queryset):
        queryset.filter(status='out_for_delivery').update(status='delivered')
        self.message_user(request, f"{queryset.count()} orders marked as delivered")