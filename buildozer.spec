[app]
title = 退貨清點APP
package.name = returnqc
package.domain = org.qc.app
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0

# 1. 指定包含 opencv (p4a 交叉編譯 recipe) 與必備庫
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
android.build_tools_version = 33.0.2
android.ndk_api = 24

# 指向 GitHub Actions 系統環境預裝的 SDK 路徑
#android.sdk_path = /usr/local/lib/android/sdk

# 2. 限制僅編譯 arm64-v8a 單一架構，大幅減少耗時與記憶體溢位 (OOM) 機率
android.archs = arm64-v8a

# 3. 指定 NDK 版本與備份選項
android.ndk = 25b
android.allow_backup = True
