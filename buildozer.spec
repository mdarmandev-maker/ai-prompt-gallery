[app]

# (str) Title of your application
title = AI Prompt Gallery

# (str) Package name
package.name = aipromptgallery

# (str) Package domain (needed for android/ios packaging)
package.domain = org.mdarman

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,ttf,otf

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = tests, bin, .buildozer, .github, .git

# (str) Application versioning
version = 0.1

# (str) Author name
author = Md Arman

# (list) Application requirements
# NOTE: pyjnius YAHAN JAAN-BOOJH KAR NAHI likha - wo Kivy ke Android
# build mein already automatically shamil hota hai (Kivy ka apna core
# dependency hai). Explicitly list karne se buildozer ek buggy pip-wheel
# install path try karta hai jo fail ho jaata hai
# ("Could not find a version that satisfies pyjnius==1.7.0").
requirements = python3,kivy,kivymd,pillow,requests,openssl,certifi,chardet,idna,urllib3

# (str) Supported orientation (portrait/landscape/all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (str) Icon of the application
icon.filename = %(source.dir)s/assets/icon.png

# (str) Presplash of the application
presplash.filename = %(source.dir)s/assets/splash.png

# (str) Presplash background color (for new android toolchain)
android.presplash_color = #0D0D14

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible
android.api = 33

# (int) Minimum API your APK / AAB will support
android.minapi = 24

# (str) Android NDK version to use - pinned so it never conflicts
# with whatever other NDK versions happen to already be on the runner
android.ndk = 25b

# (bool) If True, then automatically accept SDK license agreements.
android.accept_sdk_license = True

# (list) Android architectures to build for
# NOTE: SIRF arm64-v8a rakha hai (armeabi-v7a hata diya) - 2 arch ek
# saath build karne se GitHub runner ka disk space + build time double
# ho raha tha, jisse build 20 min chal ke fail ho raha tha. arm64-v8a
# akela hi 95%+ modern Android phones (2018+) cover karta hai. Ek baar
# APK successfully ban jaye, chaho to armeabi-v7a wapas add kar sakte
# ho (bas is line mein ", armeabi-v7a" jod dena).
android.archs = arm64-v8a

# (bool) Enable AndroidX support
android.enable_androidx = True

# (bool) Whether the app allows automatic backup of its data (Android default)
android.allow_backup = True


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
