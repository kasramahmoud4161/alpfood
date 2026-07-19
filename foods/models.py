from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

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
    category = models.ForeignKey(FoodCategory, on_delete=models.PROTECT, related_name='foods')
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES, default='lunch', db_index=True)
    
    description = models.TextField(verbose_name="توضیحات")
    ingredients = models.TextField(verbose_name="مواد اولیه", help_text="مواد تشکیل دهنده با جزئیات")
    allergens = models.CharField(max_length=300, blank=True, help_text="مواد حساسیت‌زا (مثل: شیر، تخم‌مرغ، گندم، مغزها)")
    
    weight_in_grams = models.PositiveIntegerField(default=250, help_text="وزن تقریبی پرس (گرم)")
    calories = models.PositiveIntegerField(help_text="کالری")
    
    protein = models.DecimalField(max_digits=5, decimal_places=1, validators=[MinValueValidator(0)])
    carbs = models.DecimalField(max_digits=5, decimal_places=1, validators=[MinValueValidator(0)])
    fat = models.DecimalField(max_digits=5, decimal_places=1, validators=[MinValueValidator(0)])
    fiber = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    sugar = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    sodium = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="قیمت (تومان)")
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name="قیمت با تخفیف")
    preparation_time = models.PositiveIntegerField(default=20, help_text="زمان آماده‌سازی (دقیقه)")
    
    is_available = models.BooleanField(default=True, verbose_name="موجود", db_index=True)
    is_featured = models.BooleanField(default=False, verbose_name="ویژه", db_index=True)
    
    image = models.ImageField(upload_to='foods/', verbose_name="تصویر اصلی", null=True, blank=True)
    thumbnail = models.ImageField(upload_to='foods/thumbnails/', null=True, blank=True)
    
    order_count = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.discount_price and self.discount_price >= self.price:
            raise ValidationError({'discount_price': 'قیمت با تخفیف باید کمتر از قیمت اصلی باشد.'})

    @property
    def final_price(self):
        return self.discount_price if self.discount_price else self.price
    
    @property
    def calories_per_gram(self):
        if self.weight_in_grams > 0:
            return round(self.calories / self.weight_in_grams, 2)
        return 0
    
    def __str__(self):
        return f"{self.name} - {self.final_price} تومان"
    
    class Meta:
        verbose_name = "غذا"
        verbose_name_plural = "غذاها"
        ordering = ['-is_available', '-order_count']