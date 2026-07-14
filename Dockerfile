# استفاده از نسخه سبک پایتون
FROM python:3.12-slim

# تنظیم متغیرهای محیطی برای عملکرد بهتر پایتون در داکر
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# تنظیم پوشه کاری داخل کانتینر
WORKDIR /app

# نصب پیش‌نیازهای سیستمی برای دیتابیس پستگرس
RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# کپی کردن فایل نیازمندی‌ها و نصب آن‌ها
COPY requirements.txt /app/

# تغییر طلایی: استفاده از سرورهای قدرتمند ایران‌سرور برای دانلود بدون نیاز به فیلترشکن
# استفاده از سرورهای قدرتمند علی‌بابا (بدون مشکل تحریم)
RUN pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# کپی کردن کل کدهای پروژه به داخل داکر
COPY . /app/