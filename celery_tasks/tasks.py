from celery import shared_task
from django.utils import timezone
from django.db.models import F, Sum, Avg
from datetime import timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


DailyReport.objects.update_or_create(
    date=today,
    defaults=stats
)
@shared_task(queue='cleanup')
def clean_expired_carts():
    """پاک کردن سبدهای خرید رها شده (بیش از ۲۴ ساعت)"""
    from orders.models import Cart
    
    # پیدا کردن سبدهایی که بیشتر از 24 ساعت از آخرین آپدیت آن‌ها گذشته است
    expiration_time = timezone.now() - timedelta(hours=24)
    expired = Cart.objects.filter(updated_at__lt=expiration_time)
    
    count = expired.count()
    if count > 0:
        expired.delete()
        logger.info(f"Cleaned {count} abandoned carts")
        
    return count

@shared_task(queue='discounts')
def apply_time_discounts():
    """اعمال تخفیف‌های زمانی (فقط روی غذاهایی که تخفیف دستی ندارند)"""
    from foods.models import Food
    
    current_hour = timezone.now().hour
    
    # شب‌ها تخفیف ویژه (20 درصد)
    # تغییر مهم: شرط discount_price__isnull=True اضافه شد تا تخفیف‌های دستی رستوران پاک نشود!
    if 20 <= current_hour <= 23:
        Food.objects.filter(discount_price__isnull=True).update(
            discount_price=F('price') * Decimal('0.8')
        )
    # ظهرها (15 درصد) فقط برای ناهار
    elif 12 <= current_hour <= 15:
        Food.objects.filter(meal_type='lunch', discount_price__isnull=True).update(
            discount_price=F('price') * Decimal('0.85')
        )
    else:
        # نکته Senior: برای پاک کردن تخفیف‌های اتوماتیک در سیستم‌های واقعی، 
        # باید یک فیلد is_auto_discount در دیتابیس داشته باشیم.
        # اینجا فعلاً به تخفیف‌ها دست نمی‌زنیم تا اطلاعات مدیر رستوران خراب نشود.
        pass

@shared_task(queue='analytics')
def calculate_daily_stats():
    """محاسبه آمار روزانه با کوئری بهینه (Performance Optimization)"""
    from orders.models import Order
    from reports.models import DailyReport
    
    today = timezone.now().date()
    orders = Order.objects.filter(
        created_at__date=today,
        status='delivered'
    )
    
    # اجرای تمام محاسبات فقط در ۱ درخواست به دیتابیس
    aggregation = orders.aggregate(
        total_rev=Sum('total_price'),
        total_cal=Sum('total_calories'),
        avg_rev=Avg('total_price')
    )
    
    stats = {
        'date': today,
        'total_orders': orders.count(),
        'total_revenue': aggregation['total_rev'] or Decimal('0.00'),
        'total_calories_sold': aggregation['total_cal'] or 0,
        'avg_order_value': aggregation['avg_rev'] or Decimal('0.00'),
    }
    
    DailyReport.objects.create(**stats)
    logger.info(f"Daily stats calculated for {today}")

# تغییر مهم: استفاده از bind=True و max_retries برای مواقعی که اینترنت سرور قطع است
@shared_task(bind=True, max_retries=3, queue='notification')
def send_daily_notifications(self):
    """ارسال اعلان روزانه با قابلیت تلاش مجدد (Retry Mechanism)"""
    from accounts.models import User
    from services.notification_service import NotificationService
    
    try:
        users = User.objects.filter(is_active=True)
        
        for user in users:
            NotificationService.send_push_notification.delay(
                user.id,
                "برنامه غذایی امروز",
                "زمان وعده‌های غذایی امروز رو بررسی کن!"
            )
    except Exception as exc:
        logger.error(f"Error sending notifications: {exc}")
        # اگر ارسال پیامک/نوتیف به دلیل قطعی شبکه فیل شد، 60 ثانیه بعد دوباره تلاش کن
        raise self.retry(exc=exc, countdown=60)