from django_filters import rest_framework as filters
from foods.models import Food

class FoodFilter(filters.FilterSet):
    min_calories = filters.NumberFilter(field_name="calories", lookup_expr='gte')
    max_calories = filters.NumberFilter(field_name="calories", lookup_expr='lte')
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
    min_rating = filters.NumberFilter(field_name="average_rating", lookup_expr='gte')
    max_preparation_time = filters.NumberFilter(field_name="preparation_time", lookup_expr='lte')
    
    class Meta:
        model = Food
        fields = ['category__diet_type', 'meal_type', 'is_featured', 'is_available']