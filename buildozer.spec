[app]

# (str) Title of your application
title = QR Scanner

# (str) Package name
package.name = qrscanner

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning (method 1)
version = 1.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3==3.9.19,kivy==2.1.0,pillow==9.5.0,pyzbar==0.1.9,gtts==2.3.2,requests==2.28.2,urllib3==1.26.15,certifi==2022.12.7,chardet==5.1.0,idna==3.4,click==8.1.3,plyer==2.1.0,pyjnius==1.4.2

# (str) Supported orientation (landscape, sensorLandscape, portrait, sensorPortrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = CAMERA,INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,RECORD_AUDIO,READ_MEDIA_AUDIO

# (int) Target Android API, should be as high as possible.
android.api = 30

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 23b

# (str) Android SDK version to use
android.sdk = 30

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = False

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
