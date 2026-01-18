from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response 
from rest_framework.permissions import IsAuthenticated, AllowAny 
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from apps.orders.models import Order
from apps.users.models import User
from apps.delivery.models import DeliveryAssignment
from apps.admin.serializers import AdminOrderSerializer, DeliveryPartnerSerializer, DashboardStatsSerializer

@api_view(['POST'])
@permission_classes([AllowAny])  # Allow unauthenticated access for login
def admin_login(request):
    """Admin login endpoint using JWT - supports both custom admin users and Django superusers"""
    username = request.data.get('username')
    password = request.data.get('password')

    try:
        # First try to find a custom admin user
        try:
            user = User.objects.get(username=username, user_type='admin')
        except User.DoesNotExist:
            # If no custom admin user found, try Django's default User model for superusers
            from django.contrib.auth import authenticate
            django_user = authenticate(username=username, password=password)
            if django_user and django_user.is_superuser:
                # Create or get corresponding custom User object
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': getattr(django_user, 'email', ''),
                        'first_name': getattr(django_user, 'first_name', ''),
                        'last_name': getattr(django_user, 'last_name', ''),
                        'user_type': 'admin'
                    }
                )
                # Update password if user was created or password doesn't match
                if created or not user.check_password(password):
                    user.set_password(password)
                    user.save()
            else:
                raise User.DoesNotExist()

        # Verify password for custom User model
        if user.check_password(password):
            from rest_framework_simplejwt.tokens import RefreshToken

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                'access': access_token,
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.get_full_name(),
                    'user_type': user.user_type
                }
            })
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        return Response({'error': 'Admin user not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders(request):
    """Get all orders with optional status filter"""
    status_filter = request.query_params.get('status')
    orders = Order.objects.select_related('customer', 'store').prefetch_related('order_items')

    if status_filter:
        orders = orders.filter(status=status_filter)

    orders = orders.order_by('-created_at')
    serializer = AdminOrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_details(request, order_id):
    """Get detailed order information"""
    try:
        order = Order.objects.select_related('customer', 'store').prefetch_related('order_items', 'delivery_assignment').get(id=order_id)
        serializer = AdminOrderSerializer(order)
        return Response(serializer.data)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_delivery_partner(request, order_id):
    """Assign a delivery partner to an order"""
    try:
        order = Order.objects.get(id=order_id)
        delivery_partner_id = request.data.get('delivery_partner_id')
    
        if not delivery_partner_id:
            return Response({'error': 'Delivery partner ID required'}, status=status.HTTP_400_BAD_REQUEST)
        
        delivery_partner = User.objects.get(id=delivery_partner_id, user_type='delivery_partner')
        
        # Create delivery assignment
        assignment, created = DeliveryAssignment.objects.get_or_create(
            order=order,
            defaults={'delivery_partner': delivery_partner}
        )

        if not created:
            assignment.delivery_partner = delivery_partner
            assignment.assigned_at = timezone.now()
            assignment.save()

        # Update order status
        order.status = 'confirmed'
        order.save()
        
        # Send notification to delivery partner
        from core.utils import send_delivery_notification
        send_delivery_notification(order, 'assigned')

        return Response({'message': 'Delivery partner assigned successfully'})

    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({'error': 'Delivery partner not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    """Update order status (for admin actions)"""
    try:
        order = Order.objects.get(id=order_id)
        new_status = request.data.get('status')

        if not new_status:
            return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)

        valid_statuses = ['confirmed', 'packed', 'out_for_delivery', 'delivered', 'cancelled']
        if new_status not in valid_statuses:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()

        # Send notifications
        from core.utils import send_order_status_notification
        send_order_status_notification(order, new_status)

        return Response({'message': f'Order status updated to {new_status}'})

    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_delivery_partners(request):
    """Get all delivery partners"""
    partners = User.objects.filter(user_type='delivery_partner')
    serializer = DeliveryPartnerSerializer(partners, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_fcm_token(request):
    """Update admin FCM token for push notifications"""
    token = request.data.get('fcm_token')
    if not token:
        return Response({'error': 'FCM token is required'}, status=status.HTTP_400_BAD_REQUEST)

    request.user.fcm_token = token
    request.user.save()

    return Response({'message': 'FCM token updated successfully'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_stats(request):
    """Get dashboard statistics"""
    # New orders in last 24 hours
    new_orders = Order.objects.filter(
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).count()

    # Active deliveries (assigned but not delivered)
    active_deliveries = DeliveryAssignment.objects.filter(
        delivered_at__isnull=True
    ).count()

    # Total revenue today
    total_revenue = Order.objects.filter(
        status='delivered',
        updated_at__date=timezone.now().date()
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Total delivery partners
    total_partners = User.objects.filter(user_type='delivery_partner').count()

    stats = {
        'new_orders': new_orders,
        'active_deliveries': active_deliveries,
        'total_revenue': total_revenue,
        'total_partners': total_partners
    }

    serializer = DashboardStatsSerializer(stats)
    return Response(serializer.data)