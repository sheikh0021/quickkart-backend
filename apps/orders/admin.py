from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'quantity', 'unit_price', 'total_price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'store', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'customer__username')
    inlines = [OrderItemInline]