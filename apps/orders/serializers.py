from rest_framework import serializers
from .models import Order, OrderItem
from apps.products.models import Product

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

class CreateOrderSerializer(serializers.Serializer):
    store_id = serializers.IntegerField()
    delivery_address = serializers.CharField()
    delivery_latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    delivery_longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField()
        )
    )

    def create(self, validated_data):
        # Order creation logic will be implemented in views
        pass