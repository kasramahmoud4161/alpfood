from rest_framework import serializers
from .models import WeeklyPlan, DailyMealPlan
from foods.serializers import FoodSerializer

class DailyMealPlanSerializer(serializers.ModelSerializer):
    food_detail = FoodSerializer(source='food', read_only=True)
    meal_type_display = serializers.CharField(source='get_meal_type_display', read_only=True)
    day_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = DailyMealPlan
        fields = [
            'id', 'day_of_week', 'day_display', 
            'meal_type', 'meal_type_display', 
            'food', 'food_detail', 'date'
        ]

class WeeklyPlanSerializer(serializers.ModelSerializer):
    daily_plans = DailyMealPlanSerializer(many=True, read_only=True)
    
    class Meta:
        model = WeeklyPlan
        fields = [
            'id', 'week_start_date', 'week_end_date', 
            'daily_plans', 'is_active', 'created_at'
        ]

class GeneratePlanSerializer(serializers.Serializer):
    start_date = serializers.DateField()
