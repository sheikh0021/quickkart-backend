from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Store, Banner
from django.db.models import Q
from .serializers import StoreSerializer, HomeResponseSerializer
import math

class StoreListView(generics.ListAPIView):
    serializer_class = StoreSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Store.objects.filter(is_active=True)

        # Filter by location (simple distance calculation)
        latitude = self.request.query_params.get('lat')
        longitude = self.request.query_params.get('lng')

        if latitude and longitude:
            try:
                user_lat = float(latitude)
                user_lng = float(longitude)

                # Filter stores within reasonable distance (simplified)
                # In production, you'd use PostGIS or a proper geospatial query
                filtered_stores = []
                for store in queryset:
                    distance = self.calculate_distance(
                        user_lat, user_lng,
                        float(store.latitude), float(store.longitude)
                    )
                    if distance <= store.delivery_radius:  # within delivery radius
                        filtered_stores.append(store.id)

                queryset = queryset.filter(id__in=filtered_stores)
            except (ValueError, TypeError):
                pass  # Invalid coordinates, return all stores

        return queryset

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points in kilometers (Haversine formula)"""
        R = 6371  # Earth's radius in kilometers

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
             * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return R * c

class StoreDetailView(generics.RetrieveAPIView):
    queryset = Store.objects.filter(is_active=True)
    serializer_class = StoreSerializer
    permission_classes = (IsAuthenticated,)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def home_view(request):
    """Home endpoint that returns stores, categories, and banners for the home screen"""
    try:
        # Get nearby stores (simplified - in production use user's location)
        stores = Store.objects.filter(is_active=True)[:20]  # Limit for performance

        # Get active banners
        banners = Banner.objects.filter(is_active=True)

        #get active categories
        from apps.products.models import Category
        categories = Category.objects.filter(is_active=True)

        # Prepare response data
        response_data = {
            'stores': stores,
            'categories': categories,
            'banners': banners,
        }

        serializer = HomeResponseSerializer(response_data)
        return Response(serializer.data)

    except Exception as e:
        return Response(
            {'error': 'Failed to load home data'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
