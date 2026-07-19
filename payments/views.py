import requests
import json
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from orders.models import Order
from .models import Payment

# تنظیمات زرین‌پال از فایل env.
MERCHANT = getattr(settings, 'ZARINPAL_MERCHANT_ID', 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx')
SANDBOX = getattr(settings, 'ZARINPAL_SANDBOX', True)

# آدرس‌های نسخه ۴ زرین‌پال
ZP_API_REQUEST = f"https://{'sandbox' if SANDBOX else 'api'}.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = f"https://{'sandbox' if SANDBOX else 'api'}.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = f"https://{'sandbox' if SANDBOX else 'www'}.zarinpal.com/pg/StartPay/"

# آدرسی که زرین‌پال بعد از پرداخت کاربر را به آن برمی‌گرداند (باید سرور بک‌اند شما باشد)
CALLBACK_URL = "http://localhost:8000/api/payments/verify/"

class PaymentStartView(APIView):
    """ارسال درخواست به زرین‌پال و دریافت لینک پرداخت"""
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        # 1. پیدا کردن سفارش متعلق به همین کاربر که هنوز پرداخت نشده است
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        if order.status != 'pending':
            return Response({"error": "این سفارش در انتظار پرداخت نیست یا قبلاً پرداخت شده است."}, status=status.HTTP_400_BAD_REQUEST)

        # 2. محاسبه مبلغ (تبدیل تومان دیتابیس به ریال برای زرین‌پال)
        amount_rial = int(order.total_price) * 10
        description = f"پرداخت سفارش شماره {order.order_number} - کاربر {request.user.username}"

        # 3. ارسال ریکوئست به سرور زرین‌پال
        data = {
            "merchant_id": MERCHANT,
            "amount": amount_rial,
            "callback_url": CALLBACK_URL,
            "description": description,
        }
        
        try:
            response = requests.post(ZP_API_REQUEST, data=json.dumps(data), headers={'content-type': 'application/json'}, timeout=10)
            result = response.json()
            
            if len(result['errors']) == 0:
                authority = result['data']['authority']
                
                # 4. ذخیره یا آپدیت رکورد پرداخت در دیتابیس
                Payment.objects.update_or_create(
                    order=order,
                    defaults={'amount': order.total_price, 'authority': authority, 'is_paid': False}
                )
                
                # 5. ارسال لینک پرداخت به فرانت‌اند (Next.js) تا کاربر را ریدایرکت کند
                payment_url = f"{ZP_API_STARTPAY}{authority}"
                return Response({"payment_url": payment_url}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "خطا در اتصال به درگاه", "details": result['errors']}, status=status.HTTP_400_BAD_REQUEST)
                
        except requests.exceptions.RequestException:
            return Response({"error": "تایم‌اوت یا خطای شبکه در ارتباط با زرین‌پال"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class PaymentVerifyView(APIView):
    """بررسی و تایید پرداخت هنگام بازگشت کاربر از درگاه"""
    permission_classes = [] # چون زرین‌پال این ریکوئست را میزند، نیازی به توکن نیست

    def get(self, request):
        authority = request.query_params.get('Authority')
        status_param = request.query_params.get('Status')

        if not authority or status_param != 'OK':
            # کاربر از درگاه انصراف داده است
            # بهتر است اینجا ریدایرکت کنید به یک صفحه ارور در Next.js
            return Response({"error": "پرداخت توسط کاربر لغو شد یا ناموفق بود."}, status=status.HTTP_400_BAD_REQUEST)

        # پیدا کردن تراکنش در دیتابیس
        payment = get_object_or_404(Payment, authority=authority)
        order = payment.order

        if payment.is_paid:
            return Response({"message": "این تراکنش قبلاً با موفقیت تایید شده است."}, status=status.HTTP_200_OK)

        # ارسال ریکوئست تایید به زرین‌پال
        data = {
            "merchant_id": MERCHANT,
            "amount": int(payment.amount) * 10, # مبلغ باید دقیقاً همانی باشد که دیتابیس ما می‌گوید (به ریال)
            "authority": authority,
        }
        
        try:
            response = requests.post(ZP_API_VERIFY, data=json.dumps(data), headers={'content-type': 'application/json'}, timeout=10)
            result = response.json()
            
            if len(result['errors']) == 0:
                # کد 100 یعنی پرداخت موفق، کد 101 یعنی قبلاً وریفای شده
                if result['data']['code'] in [100, 101]:
                    ref_id = result['data']['ref_id']
                    
                    # === تراکنش اتمیک: آپدیت همزمان تراکنش و سفارش ===
                    with transaction.atomic():
                        payment.is_paid = True
                        payment.ref_id = ref_id
                        payment.save()
                        
                        order.status = 'paid'
                        order.save(update_fields=['status'])
                    
                    # اینجا در پروژه واقعی باید کاربر را به فرانت‌اند (مسیر موفقیت) ریدایرکت کنید
                    # redirect(f"http://localhost:3000/payment-success?ref={ref_id}")
                    return Response({
                        "message": "پرداخت با موفقیت انجام شد",
                        "ref_id": ref_id,
                        "order_number": order.order_number
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "تراکنش ناموفق", "code": result['data']['code']}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "تراکنش ناموفق از سمت زرین‌پال"}, status=status.HTTP_400_BAD_REQUEST)
                
        except requests.exceptions.RequestException:
            return Response({"error": "خطا در ارتباط با سرور زرین‌پال برای تایید پرداخت"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)