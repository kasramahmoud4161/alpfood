from django.db import models
from django.conf import settings

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    food = models.ForeignKey("foods.Food", on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'food']
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # به‌روزرسانی میانگین امتیاز غذا
        from django.db.models import Avg
        avg_rating = Review.objects.filter(food=self.food).aggregate(Avg('rating'))['rating__avg']
        self.food.average_rating = avg_rating
        self.food.save(update_fields=['average_rating'])
    
    def __str__(self):
        return f"{self.user.phone} - {self.food.name}: {self.rating}⭐"