from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from django.db.models import Q

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)

class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True)

        #filter by store
        store_id = self.request.query_params.get('store')
        if store_id:
            queryset = queryset.filter(store_id=store_id)

        #filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset =queryset.filter(category_id=category_id)

        #search by name or description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
            return queryset
        
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)