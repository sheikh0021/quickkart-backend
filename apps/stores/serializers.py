from rest_framework import serializers
from .models import Store, Banner
from apps.products.models import Category

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'

class HomeResponseSerializer(serializers.Serializer):
    stores = StoreSerializer(many=True)
    categories = serializers.SerializerMethodField()
    banners = BannerSerializer(many=True)

    def get_categories(self, obj):
        categories = Category.objects.filter(is_active=True)
        return CategorySerializer(categories, many=True).data

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'