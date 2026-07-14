from celery import shared_task
from django.utils import timezone
from django.core.cache import cache
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

@shared_task(queue='cleanup')
def clean_expired_carts():
    """پاک کردن سبدهای خرید منقضی شده"""
    from apps.orders.models import Cart
    expired = Cart.objects.filter(expires_at__lt=timezone.now())
    count = expired.count()
    expired.delete()
    logger.info(f"Cleaned {count} expired carts")
    return count

@shared_task(queue='discounts')
def apply_time_discounts():
    """اعمال تخفیف‌های زمانی"""
    from foods.models import Food
    
    current_hour = timezone.now().hour
    
    # شب‌ها تخفیف ویژه
    if 20 <= current_hour <= 23:
        Food.objects.update(discount_price=models.F('price') * Decimal('0.8'))
    elif 12 <= current_hour <= 15:  # ظهر
        Food.objects.filter(meal_type='lunch').update(discount_price=models.F('price') * Decimal('0.85'))
    else:
        Food.objects.filter(discount_price__isnull=False).update(discount_price=None)

@shared_task(queue='analytics')
def calculate_daily_stats():
    """محاسبه آمار روزانه"""
    from apps.orders.models import Order
    from apps.reports.models import DailyReport
    
    today = timezone.now().date()
    orders = Order.objects.filter(
        created_at__date=today,
        status='delivered'
    )
    
    stats = {
        'date': today,
        'total_orders': orders.count(),
        'total_revenue': orders.aggregate(Sum('total_price'))['total_price__sum'] or 0,
        'total_calories_sold': orders.aggregate(Sum('total_calories'))['total_calories__sum'] or 0,
        'avg_order_value': orders.aggregate(Avg('total_price'))['total_price__avg'] or 0,
    }
    
    DailyReport.objects.create(**stats)
    logger.info(f"Daily stats calculated for {today}")

@shared_task(queue='notification')
def send_daily_notifications():
    """ارسال اعلان روزانه"""
    from apps.accounts.models import User
    from services.notification_service import NotificationService
    
    users = User.objects.filter(is_active=True)
    
    for user in users:
        NotificationService.send_push_notification.delay(
            user.id,
            "برنامه غذایی امروز",
            "زمان وعده‌های غذایی امروز رو بررسی کن!"
        )