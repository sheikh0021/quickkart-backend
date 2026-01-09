from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from .models import Order, OrderItem
from .serializers import OrderSerializer, CreateOrderSerializer
from apps.products.models import Product
from apps.users.models import Address
from core.utils import send_order_status_notification
import uuid

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)

class CreateOrderView(generics.CreateAPIView):
    serializer_class = CreateOrderSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Generate order number
        order_number = f"QK{uuid.uuid4().hex[:8].upper()}"

        # Get validated data from serializer
        address_id = serializer.validated_data['address_id']
        notes = serializer.validated_data.get('notes', '')
        payment_method = serializer.validated_data.get('payment_method', 'COD').lower()  # ✅ Extract from request

        # Get address and determine store from items
        address = Address.objects.get(id=address_id, user=request.user)
        store = serializer.validated_items[0]['product'].store  # All items should be from same store

        # Create order
        order = Order.objects.create(
            customer=request.user,
            store=store,
            order_number=order_number,
            total_amount=serializer.total_amount,
            delivery_address=f"{address.street}, {address.city}, {address.state} - {address.zip_code}",
            delivery_latitude=address.latitude,
            delivery_longitude=address.longitude,
            payment_method=payment_method,  # ✅ Use from request (defaults to 'cod' if not provided)
            status='placed'
        )

        # Create order items
        for item_data in serializer.validated_items:
            OrderItem.objects.create(
                order=order,
                product=item_data['product'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_price=item_data['total_price']
            )

            # Update product stock
            product = item_data['product']
            product.stock_quantity -= item_data['quantity']
            product.save()

        # ✅ Refresh order from database to ensure items relationship is loaded
        order.refresh_from_db()
        send_order_status_notification(order, 'placed')
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    """Update order status (for admin/store operations)"""
    try:
        order = Order.objects.get(id=order_id)

        new_status = request.data.get('status')
        valid_statuses = ['confirmed', 'packed', 'out_for_delivery', 'delivered', 'cancelled']

        if new_status not in valid_statuses:
            return Response({'error': f'Invalid status. Must be one of: {",".join(valid_statuses)}'},
                                status=status.HTTP_400_BAD_REQUEST
                                )
        old_status = order.status
        order.status = new_status
        order.save()

        if new_status in ['packed', 'out_for_delivery', 'delivered']:
           send_order_status_notification(order, 'packed' if new_status == 'packed' else new_status)

        return Response({
                'message': f'Order status updated from {old_status} to {new_status}',
                'order_id': order.id,
                'order_number': order.order_number
            })
    except Order.DoesNotExist:
         return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )