from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from foods.serializers import FoodSerializer  # تغییر مسیر

class CartItemSerializer(serializers.ModelSerializer):
    food_detail = FoodSerializer(source='food', read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'food', 'food_detail', 'quantity', 'total_price']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_calories = serializers.IntegerField(read_only=True)
    items_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'total_calories', 'items_count', 'created_at']

class AddToCartSerializer(serializers.Serializer):
    food_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, max_value=99)

class OrderItemSerializer(serializers.ModelSerializer):
    food_name = serializers.CharField(source='food.name', read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'food', 'food_name', 'quantity', 'price_at_time', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'total_price', 'total_calories', 
            'status', 'status_display', 'delivery_address', 'delivery_time',
            'special_requests', 'items', 'created_at'
        ]