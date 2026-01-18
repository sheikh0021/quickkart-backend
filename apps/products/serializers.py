from rest_framework import serializers
from .models import Category, Product
from django.conf import settings

class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            return f"{settings.SITE_URL}{settings.MEDIA_URL}{obj.image}"
        return None

    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            return f"{settings.SITE_URL}{settings.MEDIA_URL}{obj.image}"
        return None

    class Meta:
        model = Product
        fields = '__all__'