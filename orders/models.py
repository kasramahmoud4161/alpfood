from django.db import models
from django.conf import settings
from foods.models import Food  # تغییر مسیر

class Cart(models.Model):
    """سبد خرید کاربر"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())
    
    @property
    def total_calories(self):
        return sum(item.total_calories for item in self.items.all())
    
    @property
    def items_count(self):
        return self.items.count()
    
    def __str__(self):
        return f"Cart of {self.user.username}"

class CartItem(models.Model):
    """آیتم داخل سبد خرید"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    @property
    def total_price(self):
        return self.food.final_price * self.quantity
    
    @property
    def total_calories(self):
        return self.food.calories * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.food.name}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('preparing', 'در حال آماده‌سازی'),
        ('delivered', 'تحویل داده شده'),
        ('cancelled', 'لغو شده'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_calories = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    delivery_address = models.TextField()
    delivery_time = models.DateTimeField(null=True, blank=True)
    special_requests = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.order_number} - {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']

class OrderItem(models.Model):
    """آیتم‌های سفارش"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)
    calories_at_time = models.IntegerField()
    
    @property
    def total_price(self):
        return self.price_at_time * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.food.name} in Order {self.order.order_number}"