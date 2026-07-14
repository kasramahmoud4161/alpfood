from .base import *

# خطایابی خاموش برای جلوگیری از نشت اطلاعات امنیتی
DEBUG = False

# دامنه‌های مجاز (آدرس سایت آلپ فود را اینجا قرار می‌دهیم)
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'alpfood.ir,www.alpfood.ir').split(',')

# تنظیمات امنیتی سخت‌گیرانه برای پروداکشن
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True

# اگر روی سرور SSL (https) دارید، این موارد را از کامنت خارج کنید:
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# فقط فرانت‌اند رسمی آلپ فود حق دارد به API ما ریکوئست بفرستد
CORS_ALLOWED_ORIGINS = [
    "https://alpfood.ir",
    "https://www.alpfood.ir",
    "https://app.alpfood.ir", # برای اپلیکیشن
]

# کش کردن داده‌ها با Redis برای سرعت فوق‌العاده بالا
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://redis:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}