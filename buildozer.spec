[app]
title = 退貨清點APP
package.name = returnqc
package.domain = org.qc.app
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0

# 清潔的依賴關係：完全移除 pyzbar
requirements = python3,kivy,pandas,openpyxl,opencv,pillow

orientation = portrait
osx.kivy_version = 2.1.0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
permissions = CAMERA, FLASHLIGHT, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.accept_sdk_license = True
android.ndk_api = 21