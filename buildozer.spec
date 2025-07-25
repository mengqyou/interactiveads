[app]
title = SuperTuxKart Mobile
package.name = supertuxkartmobile
package.domain = org.interactiveads

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

requirements = python3,kivy

[buildozer]
log_level = 2

# (int) Target Android API, should be as high as possible.
android.api = 28

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 23b

# (int) Android NDK API to use. This is the minimum API your app will support, it should usually match android.minapi.
android.ndk_api = 21

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = armeabi-v7a

# (bool) If True, then skip trying to update the Android sdk
android.skip_update = True

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True