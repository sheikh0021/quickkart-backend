from django.shortcuts import render
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from .models import DeliveryAssignment, LocationUpdate
from .serializers import DeliveryAssignmentSerializer, LocationUpdateSerializer
from apps.orders.models import Order

class DeliveryAssignmentListView(generics.ListAPIView):
    serializer_class = DeliveryAssignmentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return DeliveryAssignment.objects.filter(delivery_partner=self.request.user)

class LocationUpdateView(generics.CreateAPIView):
    serializer_class = LocationUpdateSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        # Add delivery partner to the data
        data = request.data.copy()
        data['delivery_partner'] = request.user.id

        # Validate that the order belongs to this delivery partner
        order_id = data.get('order')
        if order_id:
            try:
                DeliveryAssignment.objects.get(
                    delivery_partner=request.user,
                    order_id=order_id
                )
            except DeliveryAssignment.DoesNotExist:
                return Response(
                    {'error': 'Order not assigned to this delivery partner'},
                    status=status.HTTP_403_FORBIDDEN
                )

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Update delivery partner's current location
        request.user.delivery_partner_profile.current_latitude = data['latitude']
        request.user.delivery_partner_profile.current_longitude = data['longitude']
        request.user.delivery_partner_profile.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_delivery_status(request, assignment_id):
    """Update delivery status (picked up, delivered)"""
    try:
        assignment = DeliveryAssignment.objects.get(
            id=assignment_id,
            delivery_partner=request.user
        )

        status_update = request.data.get('status')
        if status_update not in ['picked_up', 'delivered']:
            return Response(
                {'error': 'Invalid status. Must be "picked_up" or "delivered"'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if status_update == 'picked_up' and not assignment.picked_up_at:
            assignment.picked_up_at = timezone.now()
            assignment.order.status = 'out_for_delivery'
        elif status_update == 'delivered' and not assignment.delivered_at:
            assignment.delivered_at = timezone.now()
            assignment.order.status = 'delivered'

        assignment.save()
        assignment.order.save()

        return Response({'status': 'updated'})

    except DeliveryAssignment.DoesNotExist:
        return Response(
            {'error': 'Delivery assignment not found'},
            status=status.HTTP_404_NOT_FOUND
        )