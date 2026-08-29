[app]
title = Echoes of Aether-9
package.name = echoesgame
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.main = game.py
version = 0.1
requirements = python3,pygame
orientation = landscape
fullscreen = 1

# Фиксация версий для предотвращения ошибок с SDK 37
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.skip_update = False

[buildozer]
log_level = 2
warn_on_root = 1
