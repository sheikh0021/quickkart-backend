from django.urls import path
from .views import StoreListView, StoreDetailView, home_view

urlpatterns = [
    path('', StoreListView.as_view(), name='store-list'),
    path('home/', home_view, name='home'),
    path('<int:pk>/', StoreDetailView.as_view(), name='store-detail'),
]