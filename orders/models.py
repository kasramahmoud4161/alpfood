from django.db import models
from django.conf import settings
from foods.models import Food
from django.db.models import Sum, F, Case, When

@property
def total_price(self):
    result = self.items.aggregate(
        total=Sum(
            F('quantity') * Case(
                When(food__discount_price__isnull=False, then=F('food__discount_price')),
                default=F('food__price')
            )
        )
    )
    return result['total'] or 0
class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def total_price(self):
        # جلوگیری از خطاهای N+1 در کوئری زدن (بهبود پرفورمنس)
        return sum(item.total_price for item in self.items.select_related('food').all())
    
    @property
    def total_calories(self):
        return sum(item.total_calories for item in self.items.select_related('food').all())
    
    @property
    def items_count(self):
        return sum(item.quantity for item in self.items.all()) # محاسبه دقیق تعداد (نه فقط ردیف‌ها)
    
    def __str__(self):
        return f"Cart of {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    food = models.ForeignKey(Food, on_delete=models.CASCADE) # در سبد خرید CASCADE منطقی است
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
    
    # تغییر مهم: حفظ تاریخچه سفارشات حتی در صورت حذف اکانت کاربر (با مقدار دهی null)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True, db_index=True)
    
    total_price = models.DecimalField(max_digits=12, decimal_places=2) # بزرگتر کردن سقف مبلغ
    total_calories = models.IntegerField(default=0)
    
    # اضافه شدن Index برای سرعت بخشیدن به داشبورد رستوران
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    
    delivery_address = models.TextField()
    delivery_time = models.DateTimeField(null=True, blank=True)
    special_requests = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        username = self.user.username if self.user else "کاربر حذف شده"
        return f"Order {self.order_number} - {username}"
    
    class Meta:
        ordering = ['-created_at']

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    # تغییر فوق‌بحرانی: جلوگیری از پاک شدن فاکتورها در صورت حذف غذا از منو
    food = models.ForeignKey(Food, on_delete=models.SET_NULL, null=True)
    food_name_snapshot = models.CharField(max_length=200, help_text="ذخیره نام غذا برای زمانی که خود غذا حذف شود")
    default='نامشخص'
    quantity = models.PositiveIntegerField()
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)
    calories_at_time = models.IntegerField()
    
    @property
    def total_price(self):
        return self.price_at_time * self.quantity
    
    def save(self, *args, **kwargs):
        # به صورت خودکار اسم غذا را اسنپ‌شات می‌گیریم تا اگر فود پاک شد اسمش در فاکتور بماند
        if self.food and not self.food_name_snapshot:
            self.food_name_snapshot = self.food.name
        super().save(*args, **kwargs)

    def __str__(self):
        name = self.food.name if self.food else self.food_name_snapshot
        return f"{self.quantity} x {name} in Order {self.order.order_number}"