from django.urls import path
from .views import PaymentStartView, PaymentVerifyView

app_name = 'payments'

urlpatterns = [
    # فرانت‌اند ID سفارش را به این مسیر پست می‌کند
    path('request/<int:order_id>/', PaymentStartView.as_view(), name='payment_start'),
    
    # زرین‌پال کلاینت را به این مسیر برمی‌گرداند
    path('verify/', PaymentVerifyView.as_view(), name='payment_verify'),
]