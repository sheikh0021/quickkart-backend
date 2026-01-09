from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'category', 'price', 'stock_quantity', 'is_available')
    list_filter = ('is_available', 'category', 'store')
    search_fields = ('name', 'description')

    list_editable = ('stock_quantity', 'is_available')

    actions = ['mark_available', 'mark_unavailable', 'restock_items']

    def mark_available(self, request, queryset):
        queryset.update(is_available=True)
        self.message_user(request, f"{queryset.count()} products marked as available.")
        mark_available.short_description = "Mark selected products as available"
    
    def mark_unavailable(self, request, queryset):
        queryset.update(is_available=False)
        self.message_user(request, f"{queryset.count()} products marked as unavailable.")
        mark_unavailable.short_description = "Mark selected products as unavailable"

    def restock_items(self, request, queryset):
        for product in queryset:
            if product.stock_quantity < 10:
                product.stock_quantity = 50
                product.save()
        self.message_user(request, f"Restored {queryset.count()} low-stock products.")
    restock_items.short_description = "Restock low-stock items (set to 50)"