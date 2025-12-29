from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import CustomerProfile, DeliveryPartnerProfile, User
from .serializers import (
    CustomerProfileSerializer,
    DeliveryPartnerProfileSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        #create profile based on user type
        if user.user_type == 'customer':
            CustomerProfile.objects.create(user=user)
        elif user.user_type == 'delivery_partner':
            DeliveryPartnerProfile.objects.create(user=user)

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user.data),
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer 

    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        user = self.request.user
        if user.user_type == 'customer':
            return CustomerProfileSerializer
        elif user.user_type == 'delivery_partner':
            return DeliveryPartnerProfileSerializer
        return UserSerializer
    
    def get_object(self):
        user = self.request.user
        if user.user_type == 'customer':
            return user.customerprofile
        elif user.user_type == 'delivery_partner':
            return user.delivery_profile
        return user