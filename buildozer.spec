[app]

# (str) Title of your application
title = یادآور

# (str) Package name
package.name = yadavar

# (str) Package domain (needed for android/ios packaging)
package.domain = org.hosein.moradi

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf,json

# (list) List of inclusions using pattern matching
source.include_patterns = fonts/*,data/*

# (str) Application versioning (method 1)
version = 1.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,plyer,jdatetime,arabic-reshaper,python-bidi,pyjnius,android,sqlite3

# (str) Supported orientation (landscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = VIBRATE,POST_NOTIFICATIONS,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
# android.ndk = 28c

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when you're sure of your local version.
# android.skip_update = False

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for continuous integration only.
android.accept_sdk_license = True

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including package of the Java package for the Application
# (this will be the Java package of the Activity class for the app)
# android.package_name = 

# (list) Android application meta-data to add (key=value format)
#android.meta_data =

# (list) Android library project to add (will be added in the
# project.properties automatically like this
# android.library_references = 

# (list) Android shared libraries which will be added to APK.
#android.add_libs = 

# (list) Gradle dependencies to add
#android.gradle_dependencies =

# (bool) Enable AndroidX support. Enable when 'android.gradle_dependencies'
# contains an 'androidx' package, or any package from Kotlin source.
#android.enable_androidx = False

# (str) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) XML file for custom backup rules (see official auto backup documentation)
# android.backup_rules =

# (str) If you need to insert variables into your AndroidManifest.xml file,
# you can do so with the manifestPlaceholders property.
# This property takes a map of key-value pairs. (via a string)
# Usage example : android.manifest_placeholders = [myCustomVariable: "myCustomValue"]
#android.manifest_placeholders = 

# (bool) Skip byte compile of pure Python modules
# android.skip_byte_compile = False

# (str) The format used to package the app for release mode (aab or apk).
# android.release_artifact = aab

# (str) The format used to package the app for debug mode (apk or aab).
android.debug_artifact = apk

#
# Python for android (p4a) specific
#

# (str) python-for-android branch to use, defaults to master
#p4a.branch = develop

# (str) python-for-android git clone directory (if empty, it will be automatically cloned from github)
#p4a.source_dir =

# (str) The directory in which python-for-android should look for your own build recipes (if any)
#p4a.local_recipes =

# (str) Filename to the hook for p4a
#p4a.hook =

# (str) Bootstrap to use for android builds
p4a.bootstrap = sdl2

# (int) port to use for serving the bootstrap
#p4a.port =

#
# iOS specific
#

# (str) Path to a custom icon
#ios.icon.iphone = 

# (str) Path to a custom icon (retina)
#ios.icon.iphone_retina = 

# (str) Path to a custom icon for iPad
#ios.icon.ipad = 

# (str) Path to a custom icon for iPad (retina)
#ios.icon.ipad_retina = 

# (str) Path to a custom icon for iPad Pro
#ios.icon.ipad_pro = 

# (list) List of iOS frameworks to include
#ios.frameworks = 

# (bool) Whether or not to sign the application
#ios.codesign = True

# (str) Path to a custom provisioning profile
#ios.provisioning_profile = 

# (str) Path to a custom code sign identity
#ios.codesign_identity = 

# (str) Path to a custom entitlements file
#ios.entitlements = 

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
# bin_dir = ./bin
icon.filename = %(source.dir)s/data/icon.png
presplash.filename = %(source.dir)s/data/presplash.png
android.presplash_color = #FFFFFF
