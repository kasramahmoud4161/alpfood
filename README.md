<div align="center">
  <img src="photo27542350370-removebg-preview.png" alt="AlpFood Logo" width="250"/>
  <h1>AlpFood Backend API 🥗🏋️‍♂️</h1>
  <p><strong>سیستم یکپارچه و هوشمند رستوران رژیمی با قابلیت تولید برنامه غذایی اختصاصی</strong></p>
  
  [![Django](https://img.shields.io/badge/Django-4.2+-092E20?style=for-the-badge&logo=django&logoColor=white)]()
  [![DRF](https://img.shields.io/badge/DRF-3.14-red?style=for-the-badge&logo=django&logoColor=white)]()
  [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)]()
  [![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white)]()
  [![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)]()
  [![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)]()
</div>

---

## 📌 معرفی پروژه (About The Project)

پروژه **آلپ فود (AlpFood)** یک بک‌اند قدرتمند توسعه‌یافته با **Django** و **Django REST Framework** است که برای مدیریت یک رستوران رژیمی مدرن طراحی شده است. 
این سیستم علاوه بر امکانات پایه‌ای مثل سفارش غذا، رزرو میز و مدیریت کاربران، دارای یک **موتور هوشمند تولید برنامه غذایی** است که بر اساس قد، وزن، هدف (کاهش، حفظ یا افزایش وزن) و میزان فعالیت کاربر، وعده‌های غذایی مناسب را پیشنهاد می‌دهد.

---

## ✨ ویژگی‌های کلیدی (Key Features)

* 🔐 **احراز هویت پیامکی:** ثبت‌نام و ورود با شماره موبایل و احراز هویت مبتنی بر JWT.
* 📊 **پروفایل سلامت:** دریافت اطلاعات فیزیکی کاربر و محاسبه خودکار کالری مورد نیاز روزانه (BMR & TDEE).
* 🥗 **منوی هوشمند غذاها:** دسته‌بندی غذاها بر اساس نوع رژیم (کتوژنیک، وگان، کم‌کالری و...) با اطلاعات دقیق ارزش غذایی.
* 📅 **برنامه غذایی خودکار:** تولید برنامه غذایی هفتگی با در نظر گرفتن کالری مجاز و حساسیت‌های غذایی کاربر.
* 🛒 **سبد خرید و سفارشات:** سیستم سفارش‌گیری با قابلیت اعتبارسنجی سقف کالری مجاز کاربر در روز.
* 🎁 **تخفیف و کوپن:** سیستم تخفیف‌های زمان‌دار (مثلاً تخفیف ویژه شبانه) و کوپن‌های اختصاصی.
* 🔔 **اعلان‌ها (Notifications):** سیستم اطلاع‌رسانی از طریق SMS، ایمیل و Push Notification با استفاده از Celery.
* 📝 **نظرات و امتیازدهی:** امکان ثبت نظر و امتیازدهی به غذاها توسط مشتریان.

---

## 🛠 تکنولوژی‌های استفاده شده (Tech Stack)

* **زبان برنامه‌نویسی:** Python 3.12
* **فریم‌ورک بک‌اند:** Django 4.2+ & Django REST Framework
* **دیتابیس:** PostgreSQL
* **صف وظایف و کش:** Celery & Redis
* **مستندسازی API:** drf-spectacular (Swagger UI & ReDoc)
* **دواپس و استقرار:** Docker, Docker-compose, Nginx, Gunicorn

---

## 🚀 راهنمای نصب و راه‌اندازی (Getting Started)

برای اجرای این پروژه روی سیستم محلی خود، مراحل زیر را دنبال کنید. سیستم برای اجرای سریع با **Docker** کانفیگ شده است.

### پیش‌نیازها
* نصب بودن [Docker](https://docs.docker.com/get-docker/) و [Docker Compose](https://docs.docker.com/compose/install/)

### اجرا با داکر (پیشنهادی)

1. کلون کردن مخزن پروژه:
   ```bash
   git clone [https://github.com/your-username/alpfood.git](https://github.com/your-username/alpfood.git)
   cd alpfood
