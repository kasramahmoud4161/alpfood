from django.contrib import admin
from django.utils.html import format_html
from .models import FoodCategory, Food

@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'diet_type_badge', 'food_count', 'description']
    list_filter = ['diet_type']
    search_fields = ['name', 'description']
    
    def diet_type_badge(self, obj):
        badges = {
            'low_cal': '🟢 کم کالری',
            'low_carb': '🟡 کم کربوهیدرات',
            'keto': '🔵 کتوژنیک',
            'vegan': '🌱 وگان',
            'gluten_free': '🍞 بدون گلوتن',
            'diabetic': '💊 دیابتی'
        }
        return badges.get(obj.diet_type, obj.diet_type)
    diet_type_badge.short_description = 'نوع رژیم'
    
    def food_count(self, obj):
        return obj.foods.count()
    food_count.short_description = 'تعداد غذاها'

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    # فیلدهایی که در لیست نمایش داده می‌شوند
    list_display = [
        'name', 'category', 'meal_type_icon', 'calories', 
        'final_price_display', 'is_available_badge', 'is_featured_badge', 
        'order_count', 'average_rating'
    ]
    
    list_filter = ['category', 'meal_type', 'is_available', 'is_featured']
    search_fields = ['name', 'description', 'ingredients']
    
    # حذف list_editable برای جلوگیری از خطا
    # اگه میخوای قابل ویرایش باشن، باید توی list_display باشن
    
    readonly_fields = ['order_count', 'average_rating', 'created_at', 'updated_at']
    
    fieldsets = (
        ('اطلاعات پایه', {
            'fields': ('name', 'category', 'meal_type', 'description', 'ingredients', 'allergens')
        }),
        ('ارزش غذایی (در هر ۱۰۰ گرم)', {
            'fields': ('calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar', 'sodium'),
            'classes': ('wide',)
        }),
        ('اطلاعات فروش', {
            'fields': ('price', 'discount_price', 'preparation_time', 'is_available', 'is_featured')
        }),
        ('تصاویر', {
            'fields': ('image', 'thumbnail'),
            'classes': ('collapse',)
        }),
        ('آمار', {
            'fields': ('order_count', 'average_rating'),
            'classes': ('collapse',)
        }),
    )
    
    def meal_type_icon(self, obj):
        icons = {
            'breakfast': '🍳 صبحانه',
            'lunch': '🍱 ناهار',
            'dinner': '🍽️ شام',
            'snack': '🥨 میان وعده'
        }
        return icons.get(obj.meal_type, obj.meal_type)
    meal_type_icon.short_description = 'وعده'
    
    def is_available_badge(self, obj):
        return '✅ موجود' if obj.is_available else '❌ ناموجود'
    is_available_badge.short_description = 'وضعیت'
    
    def is_featured_badge(self, obj):
        return '⭐ ویژه' if obj.is_featured else '-'
    is_featured_badge.short_description = 'ویژه'
    
    def final_price_display(self, obj):
        if obj.discount_price:
            return format_html('<span style="color: red;">{} تومان</span> <del>{}</del>', 
                             obj.discount_price, obj.price)
        return f"{obj.price} تومان"
    final_price_display.short_description = 'قیمت نهایی'