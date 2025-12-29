from rest_framework import serializers
from .models import DeliveryAssignment, LocationUpdate

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