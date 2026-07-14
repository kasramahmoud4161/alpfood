from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class FoodCategory(models.Model):
    DIET_TYPES = [
        ('low_cal', 'کم کالری'),
        ('low_carb', 'کم کربوهیدرات'),
        ('keto', 'کتوژنیک'),
        ('vegan', 'وگان'),
        ('gluten_free', 'بدون گلوتن'),
        ('diabetic', 'مناسب دیابتی‌ها'),
        ('paleo', 'پالئو'),
        ('mediterranean', 'مدیترانه‌ای'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="نام دسته")
    diet_type = models.CharField(max_length=20, choices=DIET_TYPES, verbose_name="نوع رژیم")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    icon = models.CharField(max_length=50, blank=True, help_text="کلاس آیکون Font Awesome")
    
    def __str__(self):
        return f"{self.name} - {self.get_diet_type_display()}"
    
    class Meta:
        verbose_name = "دسته غذایی"
        verbose_name_plural = "دسته‌های غذایی"

class Food(models.Model):
    MEAL_TYPES = [
        ('breakfast', '🍳 صبحانه'),
        ('lunch', '🍱 ناهار'),
        ('dinner', '🍽️ شام'),
        ('snack', '🥨 میان وعده'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="نام غذا")
    category = models.ForeignKey(FoodCategory, on_delete=models.CASCADE, related_name='foods')
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES, default='lunch')
    
    description = models.TextField(verbose_name="توضیحات")
    ingredients = models.TextField(verbose_name="مواد اولیه", help_text="مواد تشکیل دهنده با جزئیات")
    allergens = models.CharField(max_length=300, blank=True, help_text="مواد حساسیت‌زا (مثل: شیر، تخم‌مرغ، گندم، مغزها)")
    
    # اطلاعات تغذیه‌ای (در هر وعده)
    calories = models.IntegerField(help_text="کالری", validators=[MinValueValidator(0)])
    protein = models.DecimalField(max_digits=5, decimal_places=1, help_text="پروتئین (گرم)")
    carbs = models.DecimalField(max_digits=5, decimal_places=1, help_text="کربوهیدرات (گرم)")
    fat = models.DecimalField(max_digits=5, decimal_places=1, help_text="چربی (گرم)")
    fiber = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, help_text="فیبر (گرم)")
    sugar = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, help_text="قند (گرم)")
    sodium = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, help_text="سدیم (میلی‌گرم)")
    
    # اطلاعات فروش
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قیمت (تومان)")
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="قیمت با تخفیف")
    preparation_time = models.IntegerField(default=20, help_text="زمان آماده‌سازی (دقیقه)")
    is_available = models.BooleanField(default=True, verbose_name="موجود")
    is_featured = models.BooleanField(default=False, verbose_name="ویژه")
    
    # تصاویر
    image = models.ImageField(upload_to='foods/', verbose_name="تصویر اصلی", null=True, blank=True)
    thumbnail = models.ImageField(upload_to='foods/thumbnails/', null=True, blank=True)
    
    # آمار
    order_count = models.IntegerField(default=0, help_text="تعداد دفعات سفارش")
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def final_price(self):
        """قیمت نهایی با احتساب تخفیف"""
        return self.discount_price if self.discount_price else self.price
    
    @property
    def calories_per_gram(self):
        """کالری به ازای هر گرم (تقریبی)"""
        return self.calories / 250  # فرض وزن تقریبی 250 گرم
    
    def __str__(self):
        return f"{self.name} - {self.calories} کالری - {self.final_price} تومان"
    
    class Meta:
        verbose_name = "غذا"
        verbose_name_plural = "غذاها"
        ordering = ['-order_count', '-created_at']