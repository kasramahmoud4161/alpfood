import logging
import google.generativeai as genai
from django.conf import settings
from trainers.models import ChatHistory

logger = logging.getLogger(__name__)

class AIDietConsultant:
    """
    سرویس هوشمند مشاوره تغذیه با استفاده از Google Gemini API
    دارای قابلیت Memory (حافظه) و مدیریت Context
    """
    
    def __init__(self):
        # کانفیگ کلید گوگل
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if api_key:
            genai.configure(api_key=api_key)
            
        # مدل flash هم بسیار سریع است و هم رایگان
        self.model_name = "gemini-1.5-flash" 

    def get_advice(self, user, user_message):
        try:
            # ۱. بازیابی تاریخچه گفتگو برای ایجاد حافظه
            history = ChatHistory.objects.filter(user=user).order_by('-created_at')[:5]
            
            # ۲. آماده‌سازی Context کاربر برای شخصی‌سازی دقیق
            user_context = (
                f"اطلاعات کاربر: وزن={user.weight}، هدف={user.get_goal_display()}، "
                f"فعالیت={user.get_activity_level_display()}، آلرژی‌ها={user.allergies}"
            )
            
            system_instruction = (
                f"تو یک مشاور تغذیه حرفه‌ای در پلتفرم دایت‌رستوران هستی. "
                f"{user_context}. با لحنی حرفه‌ای، علمی و همدلانه پاسخ بده. "
                "فقط در مورد تغذیه و سلامت مشاوره بده و اگر کاربر سوال غیرمرتبط پرسید، مودبانه او را به مسیر اصلی هدایت کن."
            )
            
            # ۳. راه‌اندازی مدل با دستورالعمل سیستمی
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_instruction
            )
            
            # ۴. تبدیل تاریخچه دیتابیس به فرمت قابل فهم برای Gemini
            formatted_history = []
            for chat in reversed(history):
                formatted_history.append({'role': 'user', 'parts': [chat.message]})
                formatted_history.append({'role': 'model', 'parts': [chat.response]})
            
            # ۵. شروع یک نشست چت با حافظه قبلی
            chat_session = model.start_chat(history=formatted_history)
            
            # ۶. ارسال پیام جدید و دریافت پاسخ
            response = chat_session.send_message(user_message)
            ai_content = response.text
            
            # ۷. ذخیره در تاریخچه برای دفعات بعدی
            ChatHistory.objects.create(user=user, message=user_message, response=ai_content)
            
            return ai_content

        except Exception as e:
            logger.error(f"Unexpected error in Gemini AI Service: {str(e)}")
            return "متأسفانه در حال حاضر ارتباط با مشاور هوشمند برقرار نیست. لطفاً بعداً تلاش کنید."