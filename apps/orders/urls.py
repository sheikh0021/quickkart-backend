from django.urls import path
from .views import OrderListView, OrderDetailView, CreateOrderView

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('create/', CreateOrderView.as_view(), name='create-order'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
]