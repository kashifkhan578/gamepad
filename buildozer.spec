[app]
title = WirelessGamepad
package.name = gamepad
package.domain = org.kashif
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,plyer
orientation = landscape
osx.python_version = 3
osx.kivy_version = 2.2.0
fullscreen = 1
android.permissions = INTERNET, VIBRATE
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.accept_sdk_license = True
android.api = 34

[buildozer]
log_level = 2
warn_on_root = 1
