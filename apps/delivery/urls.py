from django.urls import path
from .views import DeliveryAssignmentListView, LocationUpdateView

urlpatterns = [
    path('assignments/', DeliveryAssignmentListView.as_view(), name='delivery-assignments'),
    path('location/', LocationUpdateView.as_view(), name='location-update'),
]