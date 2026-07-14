from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['phone', 'display_name', 'weight', 'height', 'goal_badge', 'daily_calorie_needs', 'is_active']
    list_filter = ['goal', 'activity_level', 'diet_type', 'is_active', 'is_staff']
    search_fields = ['phone', 'first_name', 'last_name']
    list_editable = ['is_active']
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('phone', 'password', 'first_name', 'last_name')
        }),
        ('اطلاعات رژیمی', {
            'fields': ('gender', 'birth_date', 'weight', 'height', 'goal', 'activity_level', 'diet_type', 'allergies'),
            'classes': ('wide',)
        }),
        ('اطلاعات تماس', {
            'fields': ('address',),
            'classes': ('collapse',)
        }),
        ('سیستم', {
            'fields': ('daily_calorie_needs', 'is_active', 'is_staff', 'is_superuser'),
            'classes': ('collapse',)
        }),
    )
    
    def display_name(self, obj):
        return f"{obj.first_name} {obj.last_name}" if obj.first_name else obj.phone
    display_name.short_description = 'نام کامل'
    
    def goal_badge(self, obj):
        colors = {
            'lose': '🔴 کاهش',
            'maintain': '⚪ حفظ',
            'gain': '🟢 افزایش'
        }
        return colors.get(obj.goal, obj.goal)
    goal_badge.short_description = 'هدف'
    
    def save_model(self, request, obj, form, change):
        if obj.pk is None:  # کاربر جدید
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)