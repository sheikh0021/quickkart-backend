from rest_framework import serializers
from .models import Order, OrderItem
from apps.products.models import Product
from apps.users.models import Address

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
    address_id = serializers.IntegerField()  # Use address from Address model
    items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField()
        )
    )
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_address_id(self, value):
        """Validate that the address belongs to the current user"""
        request = self.context.get('request')
        if request and request.user:
            try:
                address = Address.objects.get(id=value, user=request.user)
                return value
            except Address.DoesNotExist:
                raise serializers.ValidationError("Address not found or doesn't belong to user")
        return value

    def validate_items(self, value):
        """Validate items and calculate totals"""
        if not value:
            raise serializers.ValidationError("At least one item is required")

        validated_items = []
        total_amount = 0

        for item in value:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)

            if not product_id or quantity <= 0:
                raise serializers.ValidationError("Invalid item data")

            try:
                product = Product.objects.get(id=product_id, is_available=True)
                if quantity > product.stock_quantity:
                    raise serializers.ValidationError(f"Insufficient stock for {product.name}")

                item_total = product.price * quantity
                total_amount += item_total

                validated_items.append({
                    'product': product,
                    'quantity': quantity,
                    'unit_price': product.price,
                    'total_price': item_total
                })
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Product with id {product_id} not found")

        # Store validated items for use in view
        self.validated_items = validated_items
        self.total_amount = total_amount
        return value