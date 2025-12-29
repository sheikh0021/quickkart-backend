from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import DeliveryAssignment, LocationUpdate
from .serializers import DeliveryAssignmentSerializer, LocationUpdateSerializer

class DeliveryAssignmentListView(generics.ListAPIView):
    serializer_class = DeliveryAssignmentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return DeliveryAssignment.objects.filter(delivery_partner=self.request.user)

class LocationUpdateView(generics.CreateAPIView):
    serializer_class = LocationUpdateSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        # Add delivery partner to the data
        data = request.data.copy()
        data['delivery_partner'] = request.user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Update delivery partner's current location
        request.user.delivery_profile.current_latitude = data['latitude']
        request.user.delivery_profile.current_longitude = data['longitude']
        request.user.delivery_profile.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)