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

# Use older, stable versions that are known to work
android.api = 28
android.minapi = 21
android.ndk = 23b
android.ndk_api = 21
android.archs = armeabi-v7a

# Skip problematic operations
android.skip_update = True
android.accept_sdk_license = True

# Force bootstrap (SDL2 is most stable)
p4a.bootstrap = sdl2