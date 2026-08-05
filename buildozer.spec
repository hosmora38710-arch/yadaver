[app]

title = یادآور
package.name = yadaver
package.domain = org.yadaver

source.dir = .
version = 1.0

requirements = python3==3.11.0,kivy==2.3.0,plyer,jdatetime,arabic-reshaper,python-bidi,pyjnius,android,sh==1.14.3

orientation = portrait
fullscreen = 0

android.api = 33
android.ndk = 23b
android.sdk = 33
android.minapi = 21
android.arch = arm64-v8a, armeabi-v7a

android.permissions = VIBRATE,POST_NOTIFICATIONS,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.allow_backup = True

android.gradle_dependencies = 

android.manifest.orientation = portrait

# آیکون و تصویر شروع
icon.filename = %(source.dir)s/data/icon.png
presplash.filename = %(source.dir)s/data/presplash.png
android.presplash_color = #FFFFFF

# فونت‌ها و دیتا
source.include_exts = py,png,jpg,kv,atlas,ttf,json
source.include_patterns = fonts/*,data/*

# تنظیمات buildozer
[buildozer]
log_level = 2
warn_on_root = 1
