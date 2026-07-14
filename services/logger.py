import logging
from django.utils import timezone
from django.conf import settings

class OrderLogger:
    """لاگ‌گیری سفارشات"""
    
    @staticmethod
    def log_order_creation(order):
        logging.info(f"Order {order.order_number} created by {order.user.phone} at {timezone.now()}")
    
    @staticmethod
    def log_order_status_change(order, old_status, new_status):
        logging.info(f"Order {order.order_number} status changed from {old_status} to {new_status}")

class UserActivityLogger:
    """لاگ فعالیت کاربران"""
    
    @staticmethod
    def log_login(user):
        logging.info(f"User {user.phone} logged in at {timezone.now()}")
    
    @staticmethod
    def log_food_search(user, query, results_count):
        logging.info(f"User {user.phone} searched for '{query}' - {results_count} results")

# تنظیمات لاگ در settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/diet_restaurant.log',
            'encoding': 'utf-8',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
        },
        'orders': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
    },
}