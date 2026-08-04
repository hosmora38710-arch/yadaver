[app]
title = Yadaver
package.name = yadaver
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json,db
version = 1.0

requirements = python3,kivy==2.3.1,kivymd==1.1.1

orientation = portrait
fullscreen = 0
icon.filename = data/icon.png
presplash.filename = data/presplash.png

# Android
android.api = 34
android.minapi = 26
android.archs = arm64-v8a
android.enable_androidx = True
android.accept_sdk_license = True

# Permissions
android.permissions = VIBRATE,WAKE_LOCK,POST_NOTIFICATIONS

[buildozer]
log_level = 2
warn_on_root = 1
icon.filename = data/icon.png 
presplash.filename = data/presplash.png 
