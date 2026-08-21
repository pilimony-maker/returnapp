[app]
title = 退貨清點APP
package.name = returnqc
package.domain = org.qc.app
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0

# 1. 指定包含 opencv (p4a 交叉編譯 recipe) 與必備庫
requirements = python3,kivy==2.3.0,numpy==1.24.3,pillow,pandas,openpyxl,opencv

orientation = portrait
osx.kivy_version = 2.3.0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
permissions = CAMERA, FLASHLIGHT, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 24
android.accept_sdk_license = True
android.build_tools_version = 33.0.2
android.ndk_api = 24

# 強制跳過 SDK 自帶更新，走橋接路徑
android.skip_update = True
android.sdk_path = /home/runner/.buildozer/android/platform/android-sdk

# 嚴格限制單一架構
android.archs = arm64-v8a

# NDK 推薦使用與目前 Python-for-Android 配方相容性最穩定的 25c
android.ndk = 25c
android.allow_backup = True
