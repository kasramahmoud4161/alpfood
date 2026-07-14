from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import WeeklyPlan
from .serializers import WeeklyPlanSerializer, GeneratePlanSerializer, DailyMealPlanSerializer
from .services import DietPlanGenerator

class GenerateWeeklyPlanView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GeneratePlanSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            start_date = serializer.validated_data['start_date']
            
            if start_date.weekday() != 0:
                return Response({
                    'error': 'تاریخ شروع باید دوشنبه باشد'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            plan = DietPlanGenerator.generate_plan(request.user, start_date)
            
            return Response({
                'message': 'برنامه غذایی هفتگی با موفقیت تولید شد',
                'plan': WeeklyPlanSerializer(plan).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CurrentPlanView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WeeklyPlanSerializer
    
    def get_object(self):
        today = timezone.now().date()
        plan = WeeklyPlan.objects.filter(
            user=self.request.user,
            week_start_date__lte=today,
            week_end_date__gte=today,
            is_active=True
        ).first()
        return plan

class TodayMealsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        meals = DietPlanGenerator.get_today_meals(request.user)
        serializer = DailyMealPlanSerializer(meals, many=True)
        
        total_calories = sum(meal.food.calories for meal in meals)
        
        return Response({
            'date': timezone.now().date(),
            'meals': serializer.data,
            'total_calories': total_calories,
            'daily_target': request.user.daily_calorie_needs or 2000,
            'remaining_calories': (request.user.daily_calorie_needs or 2000) - total_calories
        })

class MyPlansView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WeeklyPlanSerializer
    
    def get_queryset(self):
        return WeeklyPlan.objects.filter(user=self.request.user).order_by('-week_start_date')