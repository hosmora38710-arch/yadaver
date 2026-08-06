[app]

title = Yadaver

package.name = yadaver
package.domain = org.example

source.dir = .

source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json,db

version = 1.0

requirements = python3,kivy==2.3.1,plyer,jdatetime,arabic-reshaper,python-bidi

orientation = portrait

fullscreen = 0

icon.filename = data/icon.png
presplash.filename = data/presplash.png

android.api = 34
android.minapi = 26
android.archs = arm64-v8a

android.enable_androidx = True
android.accept_sdk_license = True

android.permissions = VIBRATE,WAKE_LOCK,POST_NOTIFICATIONS

[buildozer]

log_level = 2
warn_on_root = 1
