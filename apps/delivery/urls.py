from django.urls import path
from .views import (
    DeliveryAssignmentListView,
    LocationUpdateView,
    DeliveryEarningsView,
    get_delivery_route,
    update_delivery_status,
    delivery_dashboard,
    update_availability,
    get_delivery_location,
)

urlpatterns = [
    path('assignments/', DeliveryAssignmentListView.as_view(), name='delivery-assignments'),
    path('assignments/<int:assignment_id>/status/', update_delivery_status, name='update-delivery-status'),
    path('location/', LocationUpdateView.as_view(), name='location-update'),
    path('earnings/', DeliveryEarningsView.as_view(), name='delivery-earnings'),
    path('dashboard/', delivery_dashboard, name='delivery-dashboard'),
    path('availability/', update_availability, name='update-availability'),
    path('assignments/<int:assignment_id>/update-status/', update_delivery_status, name='update-delivery-status'),
    path('orders/<int:order_id>/location/', get_delivery_location, name='delivery-location'),
    path('orders/<int:order_id>/route/', get_delivery_route, name='delivery-route'),
]