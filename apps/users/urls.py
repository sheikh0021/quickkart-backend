from django.urls import path
from .views import RegisterView, LoginView, ProfileView, AddressListView, AddressDetailView, change_password_view, logout_view, update_fcm_token

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', change_password_view, name='change-password'),
    path('logout/', logout_view, name='logout'),
    path('addresses/', AddressListView.as_view(), name='address-list'),
    path('addresses/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),
    path('update-fcm-token/', update_fcm_token, name='update-fcm-token'),
]