from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FoodViewSet, FoodCategoryViewSet

router = DefaultRouter()
router.register(r'foods', FoodViewSet, basename='food')
router.register(r'categories', FoodCategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]