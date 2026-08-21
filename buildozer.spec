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

# 1. 核心修復：雙重指定 NDK 版本，防止 Buildozer 偷偷下載 r28c
android.ndk = 25c
android.ndk_version = 25c

# 2. 強制指定 python-for-android 使用最穩定的 master 分支配方來編譯 opencv / pandas
p4a.branch = master

# 3. 嚴格限制單一架構
android.archs = arm64-v8a

# 4. 保持跳過 SDK 內建更新
android.skip_update = True
android.sdk_path = /home/runner/.buildozer/android/platform/android-sdk
android.allow_backup = True
