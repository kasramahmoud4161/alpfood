from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

class UserManager(BaseUserManager):
     
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('شماره تلفن الزامی است')
        
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(phone, password, **extra_fields)

class User(AbstractUser):
    # حذف email به عنوان فیلد اجباری
    email = models.EmailField(blank=True, null=True)
    
    # اضافه کردن شماره تلفن به عنوان فیلد اصلی
    phone_regex = RegexValidator(
        regex=r'^09[0-9]{9}$',
        message="شماره تلفن باید با 09 شروع شود و 11 رقم باشد"
    )
    phone = models.CharField(
        validators=[phone_regex],
        unique=True,
        max_length=11,
        verbose_name="شماره تلفن"
    )
    
    # حذف username و استفاده از phone به عنوان شناسه
    username = models.CharField(max_length=150, blank=True, null=True)
    
    # اطلاعات شخصی
    GENDER_CHOICES = [
        ('M', 'مرد'),
        ('F', 'زن'),
    ]
    
    GOAL_CHOICES = [
        ('lose', 'کاهش وزن 🏃‍♂️'),
        ('maintain', 'حفظ وزن ⚖️'),
        ('gain', 'افزایش وزن 💪'),
    ]
    
    ACTIVITY_LEVELS = [
        ('sedentary', 'کم تحرک'),
        ('light', 'تحرک کم'),
        ('moderate', 'تحرک متوسط'),
        ('very', 'تحرک زیاد'),
        ('extra', 'تحرک خیلی زیاد'),
    ]
    
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES, default='maintain')
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_LEVELS, default='moderate')
    diet_type = models.CharField(max_length=50, blank=True)
    allergies = models.TextField(blank=True, help_text="مواد حساسیت‌زا (مثلاً: شیر، گردو)")
    
    # سیستم
    daily_calorie_needs = models.IntegerField(null=True, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'phone'  # استفاده از شماره تلفن به جای username
    REQUIRED_FIELDS = []  # فیلدهای اجباری برای createsuperuser
    
    objects = UserManager()
    
    def calculate_calorie_needs(self):
        """محاسبه کالری مورد نیاز"""
        if not all([self.weight, self.height, self.birth_date, self.gender]):
            return 2000
        
        from datetime import date
        age = date.today().year - self.birth_date.year
        
        if self.gender == 'M':
            bmr = 10 * float(self.weight) + 6.25 * float(self.height) - 5 * age + 5
        else:
            bmr = 10 * float(self.weight) + 6.25 * float(self.height) - 5 * age - 161
        
        activity_factors = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'very': 1.725,
            'extra': 1.9
        }
        
        tdee = bmr * activity_factors[self.activity_level]
        
        if self.goal == 'lose':
            return int(tdee - 500)
        elif self.goal == 'gain':
            return int(tdee + 300)
        return int(tdee)
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.phone
        self.daily_calorie_needs = self.calculate_calorie_needs()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.phone} - {self.get_goal_display()}"
    
    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"