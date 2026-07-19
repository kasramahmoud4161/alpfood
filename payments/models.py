from django.db import models
from orders.models import Order

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.PROTECT, related_name='payment')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="مبلغ تراکنش (تومان)")
    authority = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name="کد ارجاع زرین‌پال")
    ref_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="کد پیگیری پرداخت")
    is_paid = models.BooleanField(default=False, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"تراکنش {self.order.order_number} - {'موفق' if self.is_paid else 'ناموفق'}"
        
    class Meta:
        verbose_name = "تراکنش"
        verbose_name_plural = "تراکنش‌ها"