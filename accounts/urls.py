from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView

app_name = 'accounts'

urlpatterns = [
    # ثبت نام کاربر جدید
    path('register/', RegisterView.as_view(), name='auth_register'),
    
    # ورود (گرفتن توکن) - جنگو به طور خودکار از شماره موبایل و پسورد استفاده می‌کند
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # رفرش کردن توکن
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]