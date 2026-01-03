from django.urls import path
from .views import DeliveryAssignmentListView, LocationUpdateView, update_delivery_status

urlpatterns = [
    path('assignments/', DeliveryAssignmentListView.as_view(), name='delivery-assignments'),
    path('assignments/<int:assignment_id>/status/', update_delivery_status, name='update-delivery-status'),
    path('location/', LocationUpdateView.as_view(), name='location-update'),
]