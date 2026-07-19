from django.db import models
from django.conf import settings

class TrainerProfile(models.Model):
    """پروفایل اصلی مربی و احراز هویت"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trainer_profile')
    is_verified = models.BooleanField(default=False, verbose_name="احراز هویت شده")
    
    bio = models.TextField(blank=True, verbose_name="بیوگرافی و تخصص‌ها")
    experience_years = models.PositiveIntegerField(default=0, verbose_name="سابقه کار (سال)")
    instagram_id = models.CharField(max_length=100, blank=True, verbose_name="آیدی اینستاگرام")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"مربی: {self.user.phone}"

class TrainerDocument(models.Model):
    """مدارک مربیگری و احکام قهرمانی مسابقات"""
    DOC_TYPES = [
        ('certificate', 'مدرک مربیگری'),
        ('award', 'حکم قهرمانی / مدال'),
        ('identity', 'مدرک هویتی'),
    ]
    
    trainer = models.ForeignKey(TrainerProfile, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200, verbose_name="عنوان مدرک (مثلاً: مقام اول بادی‌بیلدینگ)")
    document_type = models.CharField(max_length=20, choices=DOC_TYPES)
    
    file = models.FileField(upload_to='trainers/documents/')
    issue_date = models.DateField(null=True, blank=True, verbose_name="تاریخ اخذ")
    
    def __str__(self):
        return f"{self.title} - {self.trainer.user.phone}"

class StudentRelationship(models.Model):
    """اتصال شاگرد به مربی"""
    trainer = models.ForeignKey(TrainerProfile, on_delete=models.CASCADE, related_name='students')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='my_trainers')
    
    start_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="شاگرد فعال")
    
    class Meta:
        unique_together = ['trainer', 'student']
        
    def __str__(self):
        return f"شاگرد {self.student.phone} برای مربی {self.trainer.user.phone}"

class StudentPlan(models.Model):
    """برنامه‌های تمرینی و غذایی (سیستمی و دست‌نویس)"""
    trainer = models.ForeignKey(TrainerProfile, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=200, verbose_name="عنوان برنامه (مثلاً: برنامه حجمی ماه اول)")
    description = models.TextField(blank=True, verbose_name="توضیحات متنی مربی")
    
    handwritten_file = models.FileField(upload_to='plans/handwritten/', null=True, blank=True, verbose_name="فایل دست‌نویس")
    
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

class TrainingSession(models.Model):
    """تایم‌های تمرین حضوری/آنلاین شاگرد با مربی"""
    STATUS_CHOICES = [
        ('scheduled', 'رزرو شده'),
        ('completed', 'انجام شد'),
        ('cancelled', 'لغو شد'),
    ]
    
    trainer = models.ForeignKey(TrainerProfile, on_delete=models.CASCADE, related_name='sessions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sessions')
    
    session_datetime = models.DateTimeField(verbose_name="تاریخ و ساعت تمرین")
    duration_minutes = models.PositiveIntegerField(default=60, verbose_name="مدت زمان (دقیقه)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    location = models.CharField(max_length=200, blank=True, verbose_name="محل تمرین (نام باشگاه یا آنلاین)")
    
class ChatHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_history')
    message = models.TextField(verbose_name="پیام کاربر")
    response = models.TextField(verbose_name="پاسخ هوش مصنوعی")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']