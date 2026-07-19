from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TrainerDashboardViewSet, StudentViewSet

router = DefaultRouter()
router.register(r'dashboard', TrainerDashboardViewSet, basename='trainer-dashboard')
router.register(r'student', StudentViewSet, basename='student-view')

urlpatterns = [
    path('', include(router.urls)),
]