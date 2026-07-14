import random
from foods.models import FoodCategory, Food

def seed_categories():
    categories = [
        ('سالاد و پیش غذا', 'low_cal', 'انواع سالادهای رژیمی'),
        ('غذاهای کتو', 'keto', 'غذاهای پرچرب و کم کربوهیدرات'),
        ('سوپ‌های رژیمی', 'vegan', 'سوپ‌های گیاهی و کم کالری'),
        ('دسرهای رژیمی', 'low_cal', 'دسرهای بدون شکر'),
    ]
    
    for name, diet, desc in categories:
        FoodCategory.objects.get_or_create(
            name=name,
            defaults={'diet_type': diet, 'description': desc}
        )

def seed_foods():
    foods_data = [
        ('سالاد سزار رژیمی', 1, 'lunch', 250, 22, 12, 14, 85000),
        ('کتو پیتزا', 2, 'dinner', 450, 28, 8, 32, 150000),
        ('سوپ جو و سبزیجات', 3, 'dinner', 180, 6, 30, 3, 65000),
    ]
    
    for name, cat_id, meal, cal, pro, carb, fat, price in foods_data:
        Food.objects.get_or_create(
            name=name,
            defaults={
                'category_id': cat_id,
                'meal_type': meal,
                'calories': cal,
                'protein': pro,
                'carbs': carb,
                'fat': fat,
                'price': price,
                'description': f'غذای خوشمزه {name}',
                'ingredients': 'مواد اولیه با کیفیت',
                'preparation_time': 20,
                'is_available': True
            }
        )

def run():
    print("در حال ایجاد دیتای نمونه...")
    seed_categories()
    seed_foods()
    print("دیتای نمونه با موفقیت ایجاد شد!")