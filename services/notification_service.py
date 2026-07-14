from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task
import requests
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """سرویس جامع اعلان‌ها"""
    
    @staticmethod
    @shared_task
    def send_sms(phone, message):
        """ارسال پیامک با Kavenegar"""
        try:
            if not settings.KAVENEGAR_API_KEY:
                logger.warning("Kavenegar API key not set")
                return
            
            url = f"https://api.kavenegar.com/v1/{settings.KAVENEGAR_API_KEY}/sms/send.json"
            data = {
                'receptor': phone,
                'message': message,
                'sender': settings.KAVENEGAR_SENDER
            }
            response = requests.post(url, data=data)
            if response.status_code == 200:
                logger.info(f"SMS sent to {phone}")
                return True
        except Exception as e:
            logger.error(f"SMS failed: {e}")
        return False
    
    @staticmethod
    @shared_task
    def send_email(to_email, subject, template_name, context):
        """ارسال ایمیل با قالب"""
        try:
            from django.template.loader import render_to_string
            html_message = render_to_string(f'emails/{template_name}.html', context)
            send_mail(
                subject=subject,
                message='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"Email sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Email failed: {e}")
        return False
    
    @staticmethod
    @shared_task
    def send_push_notification(user_id, title, message):
        """ارسال نوتیفیکیشن پوش (WebSocket)"""
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            {
                'type': 'notification',
                'title': title,
                'message': message,
                'timestamp': str(timezone.now()),
            }
        )
    
    @staticmethod
    def send_order_confirmation(order):
        """ارسال تاییدیه سفارش از همه روش‌ها"""
        user = order.user
        context = {
            'order_number': order.order_number,
            'total_price': order.total_price,
            'estimated_delivery': order.estimated_delivery_time,
        }
        
        if user.phone:
            NotificationService.send_sms.delay(
                user.phone,
                f"سفارش شما با شماره {order.order_number} ثبت شد. مبلغ: {order.total_price} تومان"
            )
        
        if user.email:
            NotificationService.send_email.delay(
                user.email,
                f"تایید سفارش #{order.order_number}",
                'order_confirmation',
                context
            )
        
        NotificationService.send_push_notification.delay(
            user.id,
            "سفارش جدید",
            f"سفارش شما با موفقیت ثبت شد. شماره پیگیری: {order.order_number}"
        )