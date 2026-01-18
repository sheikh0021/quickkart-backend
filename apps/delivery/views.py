from django.shortcuts import render
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from .models import DeliveryAssignment, LocationUpdate, DeliveryEarnings
from .serializers import DeliveryAssignmentSerializer, LocationUpdateSerializer, DeliveryEarningsSerializer
from datetime import datetime, timedelta
from django.db.models import Sum
from apps.orders.models import Order
from core.utils import send_order_status_notification
from .permissions import IsDeliveryPartner

class DeliveryAssignmentListView(generics.ListAPIView):
    serializer_class = DeliveryAssignmentSerializer
    permission_classes = (IsAuthenticated, IsDeliveryPartner)

    def get_queryset(self):
        return DeliveryAssignment.objects.filter(delivery_partner=self.request.user)

class LocationUpdateView(generics.CreateAPIView):
    serializer_class = LocationUpdateSerializer
    permission_classes = (IsAuthenticated, IsDeliveryPartner)

    def create(self, request, *args, **kwargs):
        try:
            # Add delivery partner to the data
            data = request.data.copy()
            data['delivery_partner'] = request.user.id

            # Validate required fields
            required_fields = ['order', 'latitude', 'longitude']
            for field in required_fields:
                if field not in data or data[field] is None:
                    return Response(
                        {'error': f'{field} field is required'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Validate latitude and longitude ranges
            try:
                lat = float(data['latitude'])
                lng = float(data['longitude'])
                if not (-90 <= lat <= 90):
                    return Response(
                        {'error': 'Latitude must be between -90 and 90'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if not (-180 <= lng <= 180):
                    return Response(
                        {'error': 'Longitude must be between -180 and 180'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Latitude and longitude must be valid numbers'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate that the order belongs to this delivery partner
            order_id = data.get('order')
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
            request.user.delivery_partner_profile.current_latitude = lat
            request.user.delivery_partner_profile.current_longitude = lng
            request.user.delivery_partner_profile.save()

            return Response({
                'message': 'Location updated successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': 'Failed to update location'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDeliveryPartner])
def update_delivery_status(request, assignment_id):
    """Update delivery status (picked up, delivered)"""
    try:
        # Validate assignment_id
        if not assignment_id or assignment_id <= 0:
            return Response(
                {'error': 'Invalid assignment ID'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get assignment and validate ownership
        assignment = DeliveryAssignment.objects.select_related('order').get(
            id=assignment_id,
            delivery_partner=request.user
        )

        status_update = request.data.get('status')
        if not status_update:
            return Response(
                {'error': 'Status field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if status_update not in ['picked_up','out_for_delivery', 'delivered']:
            return Response(
                {'error': 'Invalid status. Must be "picked_up", "out_for_delivery", or "delivered"'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate status transitions
        if status_update == 'picked_up':
            if assignment.picked_up_at:
                return Response(
                    {'error': 'Order already marked as picked up'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if assignment.delivered_at:
                return Response(
                    {'error': 'Cannot pick up already delivered order'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            assignment.picked_up_at = timezone.now()
            assignment.order.status = 'picked_up'

        elif status_update == 'out_for_delivery':
            if not assignment.picked_up_at:
                return Response(
                    {'error': 'Order must be picked up before marking as out for delivery'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if assignment.delivered_at:
                return Response(
                    {'error': 'Cannot mark delivered order as out for delivery'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Update order status to out_for_delivery
            assignment.order.status = 'out_for_delivery'

        elif status_update == 'delivered':
            if not assignment.picked_up_at:
                return Response(
                    {'error': 'Order must be picked up before marking as delivered'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if assignment.delivered_at:
                return Response(
                    {'error': 'Order already marked as delivered'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            assignment.delivered_at = timezone.now()
            assignment.order.status = 'delivered'

            # Create earnings record for completed delivery
            DeliveryEarnings.objects.create(
                delivery_partner=assignment.delivery_partner,
                assignment=assignment,
                amount=assignment.order.delivery_fee
            )

        assignment.save()
        assignment.order.save()

        # Send notification to customer and admin
        send_order_status_notification(assignment.order, status_update)

        return Response({
            'status': 'updated',
            'message': f'Order status updated to {status_update.replace("_", " ")}',
            'assignment_id': assignment_id
        })

    except DeliveryAssignment.DoesNotExist:
        return Response(
            {'error': 'Delivery assignment not found or access denied'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': 'An unexpected error occurred'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class DeliveryEarningsView(generics.ListAPIView):
    serializer_class = DeliveryEarningsSerializer
    permission_classes = (IsAuthenticated, IsDeliveryPartner)

    def get_queryset(self):
        return DeliveryEarnings.objects.filter(delivery_partner=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDeliveryPartner])
def delivery_dashboard(request):
    """Get delivery partner dashboard with earnings summary and stats"""
    user = request.user
    now = timezone.now()

    # Today's earnings
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_earnings = DeliveryEarnings.objects.filter(
        delivery_partner=user,
        earned_at__gte=today_start
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Weekly earnings (last 7 days)
    week_start = now - timedelta(days=7)
    weekly_earnings = DeliveryEarnings.objects.filter(
        delivery_partner=user,
        earned_at__gte=week_start
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Monthly earnings (last 30 days)
    month_start = now - timedelta(days=30)
    monthly_earnings = DeliveryEarnings.objects.filter(
        delivery_partner=user,
        earned_at__gte=month_start
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Total earnings
    total_earnings = DeliveryEarnings.objects.filter(
        delivery_partner=user
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Assignment stats
    total_assignments = DeliveryAssignment.objects.filter(delivery_partner=user).count()
    completed_assignments = DeliveryAssignment.objects.filter(
        delivery_partner=user,
        delivered_at__isnull=False
    ).count()

    # Active assignments
    active_assignments = DeliveryAssignment.objects.filter(
        delivery_partner=user,
        delivered_at__isnull=True
    ).count()

    return Response({
        'earnings': {
            'today': float(today_earnings),
            'weekly': float(weekly_earnings),
            'monthly': float(monthly_earnings),
            'total': float(total_earnings)
        },
        'stats': {
            'total_assignments': total_assignments,
            'completed_deliveries': completed_assignments,
            'active_assignments': active_assignments
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDeliveryPartner])
def update_availability(request):
    """Update delivery partner availability status"""
    try:
        is_available = request.data.get('is_available')
        if is_available is None:
            return Response(
                {'error': 'is_available field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(is_available, bool):
            return Response(
                {'error': 'is_available must be a boolean'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update availability status
        request.user.delivery_partner_profile.is_available = is_available
        request.user.delivery_partner_profile.save()

        return Response({
            'message': f'Availability updated to {"available" if is_available else "unavailable"}',
            'is_available': is_available
        })

    except Exception as e:
        return Response(
            {'error': 'Failed to update availability'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )