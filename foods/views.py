from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .models import Food, FoodCategory
from .serializers import FoodSerializer, FoodCategorySerializer
from .filters import FoodFilter

class FoodCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet برای مدیریت دسته‌بندی‌های غذایی با قابلیت جستجو
    """
    queryset = FoodCategory.objects.all()
    serializer_class = FoodCategorySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['diet_type']


class FoodViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet بهینه شده برای غذاها با استفاده از FilterSet اختصاصی
    """
    serializer_class = FoodSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # استفاده از کلاس فیلتر اختصاصی که خودتان نوشته بودید
    filterset_class = FoodFilter 
    
    search_fields = ['name', 'description', 'ingredients']
    ordering_fields = ['calories', 'price', 'preparation_time', 'order_count', 'average_rating']
    ordering = ['-order_count']

    def get_queryset(self):
        # استفاده از select_related برای جلوگیری از مشکل N+1 Query
        queryset = Food.objects.select_related('category').filter(is_available=True)
        
        # فیلتر کردن آلرژی‌های کاربر در صورت لاگین بودن
        if self.request.user.is_authenticated and self.request.user.allergies:
            allergies_list = [a.strip() for a in self.request.user.allergies.split(',')]
            for allergy in allergies_list:
                queryset = queryset.exclude(allergens__icontains=allergy)
        
        return queryset

    # کش کردن نتایج برای افزایش پرفورمنس (۶۰ دقیقه)
    @method_decorator(cache_page(60 * 60))
    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        foods_qs = self.get_queryset()
        
        avg_calories = foods_qs.aggregate(Avg('calories'))['calories__avg']
        
        stats = {
            'total_foods': foods_qs.count(),
            'total_categories': FoodCategory.objects.count(),
            'avg_calories': round(avg_calories, 1) if avg_calories else 0,
            'most_ordered': FoodSerializer(foods_qs.order_by('-order_count')[:5], many=True).data,
            'featured': FoodSerializer(foods_qs.filter(is_featured=True)[:10], many=True).data,
        }
        return Response(stats)

    @method_decorator(cache_page(60 * 30))
    @action(detail=False, methods=['get'], url_path='by-diet')
    def by_diet(self, request):
        diet_groups = {}
        diet_display = dict(FoodCategory.DIET_TYPES)
        
        for diet_type, _ in FoodCategory.DIET_TYPES:
            foods = Food.objects.select_related('category').filter(
                category__diet_type=diet_type, 
                is_available=True
            )[:10]
            if foods.exists():
                diet_groups[diet_display.get(diet_type, diet_type)] = FoodSerializer(foods, many=True).data
        
        return Response(diet_groups)

    @action(detail=False, methods=['get'], url_path='recommended')
    def recommended(self, request):
        user = request.user
        base_qs = Food.objects.select_related('category').filter(is_available=True)
        
        if not user.is_authenticated:
            foods = base_qs.filter(is_featured=True)[:10]
        else:
            if user.goal == 'lose':
                foods = base_qs.filter(calories__lte=400)[:10]
            elif user.goal == 'gain':
                foods = base_qs.filter(calories__gte=400)[:10]
            else:
                foods = base_qs.order_by('-order_count')[:10]
        
        return Response(self.get_serializer(foods, many=True).data)