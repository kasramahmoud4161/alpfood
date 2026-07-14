from datetime import datetime, timedelta
from foods.models import Food

class DiscountService:
    """سیستم تخفیف خودکار"""
    
    @staticmethod
    def apply_time_based_discounts():
        """تخفیف بر اساس زمان روز"""
        current_hour = datetime.now().hour
        
        if 20 <= current_hour <= 23:  # شب‌ها تخفیف ویژه
            Food.objects.filter(is_available=True).update(discount_price=models.F('price') * 0.8)
        elif 12 <= current_hour <= 15:  # ظهرها
            Food.objects.filter(meal_type='lunch').update(discount_price=models.F('price') * 0.85)
        else:
            # حذف تخفیف‌های موقتی
            Food.objects.filter(discount_price__isnull=False).update(discount_price=None)
    
    @staticmethod
    def get_bulk_discount(quantity):
        """تخفیف تعداد"""
        if quantity >= 5:
            return 0.15  # ۱۵٪ تخفیف
        elif quantity >= 3:
            return 0.10  # ۱۰٪ تخفیف
        return 0