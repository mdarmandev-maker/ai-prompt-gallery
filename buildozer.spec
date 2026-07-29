[app]
# (str) Title of your application
title = AI Prompt Gallery
orientation = portrait
fullscreen = 0

# (str) Package name
package.name = aipromptgallery

# (str) Package domain
package.domain = org.mdarman

# (str) Source code where the main.py live
source.dir = .

# (str) Application versioning
version = 0.1

# (str) Author name
author = Md Arman

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,json

# (list) Application requirements
requirements = python3,kivy,kivymd,pillow,requests

# (str) Icon of the application
icon.filename = %(source.dir)s/assets/icon.png

# (str) Presplash of the application
presplash.filename = %(source.dir)s/assets/splash.png

# (list) Permissions
android.permissions = INTERNET
# NDK aur SDK versions fixed (Gradle error fix karne ke liye)
android.ndk = 25b
android.sdk = 33
android.api = 33
android.minapi = 24

# (list) Sirf arm64-v8a target karna - 99% modern phones isi par chalte
# hain. Dono architectures (arm64-v8a + armeabi-v7a) include karne se
# APK size lagbhag double ho jata hai. Bina isके APK size kaafi bada hoga.
android.archs = arm64-v8a
