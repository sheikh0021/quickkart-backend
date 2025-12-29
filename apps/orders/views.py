from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Order, OrderItem
from .serializers import OrderSerializer, CreateOrderSerializer
from apps.products.models import Product
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

        # Calculate total
        items_data = serializer.validated_data['items']
        total_amount = 0
        order_items = []

        for item_data in items_data:
            product = Product.objects.get(id=item_data['product_id'])
            quantity = item_data['quantity']
            total_price = product.price * quantity
            total_amount += total_price

            order_items.append({
                'product': product,
                'quantity': quantity,
                'unit_price': product.price,
                'total_price': total_price
            })

        # Create order
        order = Order.objects.create(
            customer=request.user,
            store_id=serializer.validated_data['store_id'],
            order_number=order_number,
            total_amount=total_amount,
            delivery_address=serializer.validated_data['delivery_address'],
            delivery_latitude=serializer.validated_data.get('delivery_latitude'),
            delivery_longitude=serializer.validated_data.get('delivery_longitude'),
        )

        # Create order items
        for item_data in order_items:
            OrderItem.objects.create(
                order=order,
                **item_data
            )

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)