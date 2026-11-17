"""Lokal ishlab chiqish muhiti sozlamalari."""
import socket

from .base import *  # noqa: F401, F403

DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() in ("1", "true", "yes")

# Lokal tarmoq (Wi-Fi) orqali telefonlardan ham tekshirish uchun
ALLOWED_HOSTS = ["*"]

for _origin in ("http://127.0.0.1:8088", "http://localhost:8088"):
    if _origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(_origin)

try:
    for _ip in socket.gethostbyname_ex(socket.gethostname())[2]:
        if _ip and not _ip.startswith("127."):
            _lan_origin = f"http://{_ip}:8088"
            if _lan_origin not in CSRF_TRUSTED_ORIGINS:
                CSRF_TRUSTED_ORIGINS.append(_lan_origin)
except OSError:
    pass

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
