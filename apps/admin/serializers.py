from rest_framework import serializers
from apps.orders.models import Order , OrderItem
from apps.delivery.models import DeliveryAssignment
from apps.users.models import User

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'quantity', 'unit_price', 'total_price']

class DeliveryAssignmentSerializer(serializers.ModelSerializer):
    delivery_partner_name = serializers.CharField(source='delivery_partner.get_full_name', read_only=True)
    delivery_partner_phone = serializers.CharField(source='delivery_partner.username', read_only=True)

    class Meta:
        model = DeliveryAssignment
        fields = ['id', 'delivery_partner_name', 'delivery_partner_phone', 'assigned_at','picked_up_at', 'delivered_at']
    
class AdminOrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    customer_phone= serializers.CharField(source='customer.username', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    order_items = OrderItemSerializer(many=True, read_only=True)
    delivery_assignment = DeliveryAssignmentSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number','customer_name', 'customer_phone', 'store_name', 'status', 'order_items',
            'total_amount','delivery_fee', 'delivery_address', 'created_at', 'updated_at', 'delivery_assignment'
        ]

class DeliveryPartnerSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    completed_deliveries = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'completed_deliveries', 'is_available']

    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_completed_deliveries(self, obj):
        return obj.deliveries.filter(delivered_at__isnull=False).count()
    
    def get_is_available(self, obj):
        active_deliveries = obj.deliveries.filter(delivered_at__isnull=True).count()
        return active_deliveries < 3

class DashboardStatsSerializer(serializers.Serializer):
    new_orders = serializers.IntegerField()
    active_deliveries = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_partners = serializers.IntegerField()
