from django.urls import path
from .views import (
    DeliveryAssignmentListView,
    LocationUpdateView,
    DeliveryEarningsView,
    update_delivery_status,
    delivery_dashboard,
    update_availability
)

urlpatterns = [
    path('assignments/', DeliveryAssignmentListView.as_view(), name='delivery-assignments'),
    path('assignments/<int:assignment_id>/status/', update_delivery_status, name='update-delivery-status'),
    path('location/', LocationUpdateView.as_view(), name='location-update'),
    path('earnings/', DeliveryEarningsView.as_view(), name='delivery-earnings'),
    path('dashboard/', delivery_dashboard, name='delivery-dashboard'),
    path('availability/', update_availability, name='update-availability'),
]