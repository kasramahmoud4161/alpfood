from datetime import timedelta
from django.utils import timezone
from foods.models import Food
from .models import WeeklyPlan, DailyMealPlan

class DietPlanGenerator:
    """تولید کننده برنامه غذایی هوشمند"""
    
    @staticmethod
    def generate_plan(user, start_date):
        """تولید برنامه غذایی هفتگی بر اساس نیازهای کاربر"""
        
        daily_calorie_target = user.daily_calorie_needs or 2000
        
        meal_distribution = {
            'breakfast': 0.25,
            'lunch': 0.35,
            'dinner': 0.25,
            'snack': 0.15
        }
        
        end_date = start_date + timedelta(days=6)
        
        # حذف برنامه قبلی
        WeeklyPlan.objects.filter(user=user, week_start_date=start_date).delete()
        
        weekly_plan = WeeklyPlan.objects.create(
            user=user,
            week_start_date=start_date,
            week_end_date=end_date
        )
        
        allergies_list = []
        if user.allergies:
            allergies_list = [a.strip() for a in user.allergies.split(',')]
        
        for day in range(7):
            current_date = start_date + timedelta(days=day)
            
            for meal_type, percentage in meal_distribution.items():
                calorie_target = int(daily_calorie_target * percentage)
                
                queryset = Food.objects.filter(
                    meal_type=meal_type,
                    is_available=True,
                    calories__lte=calorie_target + 100,
                    calories__gte=calorie_target - 100
                )
                
                for allergy in allergies_list:
                    queryset = queryset.exclude(allergens__icontains=allergy)
                
                food = queryset.order_by('?').first()
                
                if not food:
                    food = Food.objects.filter(
                        meal_type=meal_type,
                        is_available=True
                    ).exclude(allergens__icontains=allergy).order_by('?').first()
                
                if food:
                    DailyMealPlan.objects.create(
                        weekly_plan=weekly_plan,
                        day_of_week=day,
                        meal_type=meal_type,
                        food=food,
                        date=current_date
                    )
        
        return weekly_plan
    
    @staticmethod
    def get_current_plan(user):
        """دریافت برنامه فعلی"""
        today = timezone.now().date()
        return WeeklyPlan.objects.filter(
            user=user,
            week_start_date__lte=today,
            week_end_date__gte=today,
            is_active=True
        ).first()
    
    @staticmethod
    def get_today_meals(user):
        """دریافت وعده‌های غذایی امروز"""
        today = timezone.now().date()
        current_plan = DietPlanGenerator.get_current_plan(user)
        
        if current_plan:
            return DailyMealPlan.objects.filter(
                weekly_plan=current_plan,
                date=today
            ).select_related('food')
        
        return []