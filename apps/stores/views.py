from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Store
from django.db.models import Q
from .serializers import StoreSerializer

class StoreListView(generics.ListAPIView):
    serializer_class = StoreSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Store.objects.filter(is_active=True)

        #filter by location 
        latitude = self.request.query_params.get('lat')
        longtitude = self.request.query_params.get('lng')

        if latitude and longtitude:
            pass

        return queryset
    
class StoreDetailView(generics.RetrieveAPIView):
    queryset = Store.objects.filter(is_active=True)
    serializer_class = StoreSerializer
    permission_classes = (IsAuthenticated,)
