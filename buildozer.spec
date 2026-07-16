[app]
title = Telegram Nick Finder
package.name = nickfinder
package.domain = uz.nickfinder
source.dir = .
source.include_exts = py,html,css,js,png,jpg,jpeg,svg,json,txt
version = 1.0.0
requirements = python3,kivy,pyjnius
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 35
android.minapi = 23
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True
android.gradle_dependencies = androidx.webkit:webkit:1.12.1

[buildozer]
log_level = 2
warn_on_root = 0
