from rest_framework import serializers
from .models import Store, Banner
from apps.products.models import Category
from django.conf import settings
from apps.products.serializers import ProductSerializer

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'

class StoreSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            return f"{settings.SITE_URL}{settings.MEDIA_URL}{obj.image}"
        return None

    class Meta:
        model = Store
        fields = '__all__'

class HomeResponseSerializer(serializers.Serializer):
    stores = StoreSerializer(many=True)
    categories = serializers.SerializerMethodField()
    banners = BannerSerializer(many=True)
    products = ProductSerializer(many=True)  # ADD THIS LINE

    def get_categories(self, obj):
        categories = Category.objects.filter(is_active=True)
        return CategorySerializer(categories, many=True).data

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'