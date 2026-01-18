from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.admin_login, name='admin_login'),
    path('orders/', views.get_orders, name='admin_orders'),
    path('orders/<int:order_id>/', views.get_order_details, name='admin_order_detail'),
    path('orders/<int:order_id>/assign-delivery/', views.assign_delivery_partner, name='assign_delivery'),
    path('orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('delivery-partners/', views.get_delivery_partners, name='delivery_partners'),
    path('update-fcm-token/', views.update_fcm_token, name='admin_update_fcm_token'),
    path('dashboard-stats/', views.get_dashboard_stats, name='dashboard_stats'),
]