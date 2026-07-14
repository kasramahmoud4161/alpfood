from rest_framework import serializers
from .models import Food, FoodCategory

class FoodCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodCategory
        fields = ['id', 'name', 'diet_type', 'icon']

class FoodSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    diet_type = serializers.CharField(source='category.diet_type', read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Food
        fields = [
            'id', 'name', 'category', 'category_name', 'diet_type',
            'meal_type', 'description', 'calories', 'protein', 'carbs', 'fat',
            'price', 'discount_price', 'final_price', 'preparation_time',
            'is_available', 'is_featured', 'image', 'order_count'
        ]