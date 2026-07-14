from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from .models import Food, FoodCategory
from .serializers import FoodSerializer, FoodCategorySerializer

class FoodCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet برای دسته‌بندی غذاها"""
    queryset = FoodCategory.objects.all()
    serializer_class = FoodCategorySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['diet_type']

class FoodViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet برای غذاها"""
    serializer_class = FoodSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__diet_type', 'meal_type', 'is_featured', 'is_available']
    search_fields = ['name', 'description', 'ingredients']
    ordering_fields = ['calories', 'price', 'preparation_time', 'order_count', 'average_rating']
    ordering = ['-order_count']
    
    def get_queryset(self):
        queryset = Food.objects.filter(is_available=True)
        
        # فیلتر بر اساس محدوده کالری
        min_cal = self.request.query_params.get('min_calories')
        max_cal = self.request.query_params.get('max_calories')
        if min_cal:
            queryset = queryset.filter(calories__gte=min_cal)
        if max_cal:
            queryset = queryset.filter(calories__lte=max_cal)
        
        # فیلتر بر اساس قیمت
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # فیلتر بر اساس زمان آماده‌سازی
        max_time = self.request.query_params.get('max_preparation_time')
        if max_time:
            queryset = queryset.filter(preparation_time__lte=max_time)
        
        # فیلتر بر اساس امتیاز
        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            queryset = queryset.filter(average_rating__gte=min_rating)
        
        # اگر کاربر لاگین کرده و آلرژی دارد
        if self.request.user.is_authenticated and self.request.user.allergies:
            allergies_list = [a.strip() for a in self.request.user.allergies.split(',')]
            for allergy in allergies_list:
                queryset = queryset.exclude(allergens__icontains=allergy)
        
        return queryset
    
    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """آمار کلی غذاها"""
        total_foods = Food.objects.filter(is_available=True).count()
        avg_calories = Food.objects.filter(is_available=True).aggregate(Avg('calories'))['calories__avg']
        
        stats = {
            'total_foods': total_foods,
            'total_categories': FoodCategory.objects.count(),
            'avg_calories': round(avg_calories, 1) if avg_calories else 0,
            'most_ordered': FoodSerializer(Food.objects.filter(is_available=True).order_by('-order_count')[:5], many=True).data,
            'featured': FoodSerializer(Food.objects.filter(is_featured=True, is_available=True)[:10], many=True).data,
        }
        return Response(stats)
    
    @action(detail=False, methods=['get'], url_path='by-diet')
    def by_diet(self, request):
        """گروه‌بندی غذاها بر اساس رژیم"""
        diet_groups = {}
        diet_display = {
            'low_cal': 'کم کالری',
            'low_carb': 'کم کربوهیدرات',
            'keto': 'کتوژنیک',
            'vegan': 'وگان',
            'gluten_free': 'بدون گلوتن',
            'diabetic': 'دیابتی',
        }
        
        for diet_type, _ in FoodCategory.DIET_TYPES:
            foods = Food.objects.filter(
                category__diet_type=diet_type, 
                is_available=True
            )[:10]
            if foods.exists():
                diet_groups[diet_display.get(diet_type, diet_type)] = FoodSerializer(foods, many=True).data
        
        return Response(diet_groups)
    
    @action(detail=False, methods=['get'], url_path='recommended')
    def recommended(self, request):
        """پیشنهاد غذا بر اساس هدف کاربر"""
        user = request.user
        
        if not user.is_authenticated:
            # برای کاربران مهمان، غذاهای ویژه رو نشون بده
            foods = Food.objects.filter(is_featured=True, is_available=True)[:10]
        else:
            if user.goal == 'lose':
                foods = Food.objects.filter(calories__lte=400, is_available=True)[:10]
            elif user.goal == 'gain':
                foods = Food.objects.filter(calories__gte=400, is_available=True)[:10]
            else:
                foods = Food.objects.filter(is_available=True).order_by('-order_count')[:10]
        
        serializer = self.get_serializer(foods, many=True)
        return Response(serializer.data)