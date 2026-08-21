[app]
title = 退貨清點APP
package.name = returnqc
package.domain = org.qc.app
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0

# 1. 修正 opencv 為 opencv-python，並加入 numpy（opencv 依賴）與 requests/certifi 確保編譯環境穩定
requirements = python3,kivy==2.3.0,numpy,pillow,pandas,openpyxl,opencv

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
android.ndk_api = 24

# 2. 限制僅編譯 arm64-v8a 單一架構，大幅減少耗時與記憶體溢位 (OOM) 機率
android.archs = arm64-v8a

# 3. 指定 NDK 版本與編譯選項
android.ndk = 25b
android.allow_backup = True
