from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
import random
import string
from .models import Cart, CartItem, Order, OrderItem
from .serializers import (
    CartSerializer, AddToCartSerializer, 
    OrderSerializer, CartItemSerializer
)
from foods.models import Food  # تغییر مسیر

class CartView(generics.RetrieveAPIView):
    """مشاهده سبد خرید"""
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

class AddToCartView(generics.GenericAPIView):
    """افزودن به سبد خرید"""
    serializer_class = AddToCartSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            food_id = serializer.validated_data['food_id']
            quantity = serializer.validated_data['quantity']
            
            food = get_object_or_404(Food, id=food_id, is_available=True)
            cart, _ = Cart.objects.get_or_create(user=request.user)
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                food=food,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            return Response({
                'message': f'{food.name} به سبد خرید اضافه شد',
                'cart': CartSerializer(cart).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RemoveFromCartView(generics.GenericAPIView):
    """حذف از سبد خرید"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, item_id):
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()
        return Response({'message': 'آیتم از سبد خرید حذف شد'})

class UpdateCartItemView(generics.GenericAPIView):
    """به‌روزرسانی تعداد آیتم در سبد خرید"""
    permission_classes = [IsAuthenticated]
    
    def put(self, request, item_id):
        quantity = request.data.get('quantity')
        if not quantity or quantity < 1:
            return Response({'error': 'تعداد نامعتبر'}, status=status.HTTP_400_BAD_REQUEST)
        
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.quantity = quantity
        cart_item.save()
        
        return Response({
            'message': 'سبد خرید به‌روزرسانی شد',
            'cart': CartSerializer(cart).data
        })

class CheckoutView(generics.GenericAPIView):
    """تسویه حساب و ایجاد سفارش"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        
        if not cart.items.exists():
            return Response({'error': 'سبد خرید خالی است'}, status=status.HTTP_400_BAD_REQUEST)
        
        total_calories = cart.total_calories
        user = request.user
        
        if user.daily_calorie_needs and total_calories > user.daily_calorie_needs:
            return Response({
                'error': f'کالری این سفارش ({total_calories}) بیشتر از نیاز روزانه شما ({user.daily_calorie_needs}) است'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        order_number = ''.join(random.choices(string.digits, k=10))
        
        order = Order.objects.create(
            user=user,
            order_number=order_number,
            total_price=cart.total_price,
            total_calories=cart.total_calories,
            delivery_address=request.data.get('delivery_address', ''),
            delivery_time=request.data.get('delivery_time'),
            special_requests=request.data.get('special_requests', '')
        )
        
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                food=cart_item.food,
                quantity=cart_item.quantity,
                price_at_time=cart_item.food.final_price,
                calories_at_time=cart_item.food.calories
            )
            
            food = cart_item.food
            food.order_count += cart_item.quantity
            food.save()
        
        cart.items.all().delete()
        
        return Response({
            'message': 'سفارش با موفقیت ثبت شد',
            'order': OrderSerializer(order).data
        }, status=status.HTTP_201_CREATED)

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """مشاهده سفارشات کاربر"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status == 'pending':
            order.status = 'cancelled'
            order.save()
            return Response({'message': 'سفارش لغو شد'})
        return Response({'error': 'امکان لغو این سفارش وجود ندارد'}, status=status.HTTP_400_BAD_REQUEST)