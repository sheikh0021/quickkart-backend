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