from rest_framework import serializers
from .models import DeliveryAssignment, LocationUpdate, DeliveryEarnings

class DeliveryAssignmentSerializer(serializers.ModelSerializer):
    order_details = serializers.SerializerMethodField()
    customer_details = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryAssignment
        fields = '__all__'

    def get_order_details(self, obj):
        return {
            'order_number': obj.order.order_number,
            'status': obj.order.status,
            'total_amount': obj.order.total_amount,
            'delivery_address': obj.order.delivery_address,
            'delivery_latitude': float(obj.order.delivery_latitude) if obj.order.delivery_latitude else None,
            'delivery_longitude': float(obj.order.delivery_longitude) if obj.order.delivery_longitude else None,
        }

    def get_customer_details(self, obj):
        return {
            'name': obj.order.customer.username,
            'phone': obj.order.customer.phone_number,
        }

class LocationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationUpdate
        fields = '__all__'


class DeliveryEarningsSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='assignment.order.order_number', read_only=True)
    earned_date = serializers.DateField(source='earned_at', read_only=True)

    class Meta:
        model = DeliveryEarnings
        fields = ['id', 'amount', 'earned_at', 'earned_date', 'order_number']