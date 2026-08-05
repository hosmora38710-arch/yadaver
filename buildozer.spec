[app]

# عنوان برنامه (روی گوشی نمایش داده می‌شود)
title = یادآور

# نام پکیج (فقط حروف کوچک و بدون فاصله)
package.name = yadavar

# دامنه پکیج (شناسه یکتا: org.example.yadavar)
package.domain = org.yadavar

# پوشه سورس
source.dir = .

# پسوند فایل‌هایی که داخل APK کپی شوند
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,otf,json,db,txt,md

# پوشه‌هایی که نباید داخل APK بروند
source.exclude_dirs = tests, bin, venv, .git, .buildozer, __pycache__

# نسخه برنامه
version = 1.0

# وابستگی‌ها (مهم)
requirements = python3,kivy==2.3.1,plyer,jdatetime,arabic-reshaper,python-bidi,pyjnius,android,pillow,openssl

# جهت صفحه
orientation = portrait

# تمام‌صفحه نباشد
fullscreen = 0

# آیکون (اگر فایل icon.png در ریشه پروژه داری)
# icon.filename = %(source.dir)s/icon.png

# پیش‌بارگذاری تصاویر
# presplash.filename = %(source.dir)s/presplash.png

# ==================================================
# تنظیمات اندروید
# ==================================================

# API هدف و حداقل
android.api = 34
android.minapi = 21
android.ndk_api = 21

# معماری‌ها (برای گوشی‌های جدید فقط arm64 کافی است)
# اگر می‌خواهی روی گوشی‌های قدیمی‌تر هم کار کند هر دو را بگذار:
android.archs = arm64-v8a

# مجوزها
android.permissions = VIBRATE,POST_NOTIFICATIONS,WAKE_LOCK,FOREGROUND_SERVICE

# فعال‌سازی AndroidX
android.enable_androidx = True

# پذیرش لایسنس SDK
android.accept_sdk_license = True

# Bootstrap
# p4a.bootstrap = sdl2

# نگه داشتن لاگ برای دیباگ
android.logcat_filters = *:S python:D

# ==================================================
# بخش Buildozer
# ==================================================

[buildozer]

# سطح لاگ (2 = جزئیات کامل)
log_level = 2

# هشدار در صورت اجرای با root
warn_on_root = 1
