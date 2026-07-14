from django.db import models
from django.conf import settings
from foods.models import Food

class WeeklyPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='weekly_plans')
    week_start_date = models.DateField()
    week_end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Weekly plan for {self.user.phone} - {self.week_start_date}"
    
    class Meta:
        ordering = ['-week_start_date']

class DailyMealPlan(models.Model):
    DAYS_OF_WEEK = [
        (0, 'دوشنبه'),
        (1, 'سه‌شنبه'),
        (2, 'چهارشنبه'),
        (3, 'پنج‌شنبه'),
        (4, 'جمعه'),
        (5, 'شنبه'),
        (6, 'یکشنبه'),
    ]
    
    MEAL_TYPES = [
        ('breakfast', 'صبحانه'),
        ('lunch', 'ناهار'),
        ('dinner', 'شام'),
        ('snack', 'میان وعده'),
    ]
    
    weekly_plan = models.ForeignKey(WeeklyPlan, on_delete=models.CASCADE, related_name='daily_plans')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    date = models.DateField()
    
    class Meta:
        unique_together = ['weekly_plan', 'day_of_week', 'meal_type']
    
    def __str__(self):
        return f"{self.get_day_of_week_display()} - {self.get_meal_type_display()}: {self.food.name}"