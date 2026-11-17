"""
Turon Odob-Ilm Raqamli Maktab Platformasi — Asosiy Django sozlamalari.
"""
import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-insecure-turon-odob-ilm-change-me-in-production-5928174",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() in ("1", "true", "yes")

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
    if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "DJANGO_CSRF_TRUSTED_ORIGINS", "http://127.0.0.1:8000,http://localhost:8000"
    ).split(",")
    if o.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    # Loyiha ilovalari
    "apps.accounts.apps.AccountsConfig",
    "apps.core.apps.CoreConfig",
    "apps.branches.apps.BranchesConfig",
    "apps.content.apps.ContentConfig",
    "apps.reviews.apps.ReviewsConfig",
    "apps.analytics.apps.AnalyticsConfig",
    "apps.reports.apps.ReportsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.analytics.middleware.PrivacyFriendlyPageViewMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Ma'lumotlar bazasi: PostgreSQL (DATABASE_URL orqali) yoki lokal SQLite
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "uz"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/boshqaruv/kirish/"
LOGIN_REDIRECT_URL = "/boshqaruv/"
LOGOUT_REDIRECT_URL = "/"

# Xavfsizlik sarlavhalari va cookie sozlamalari
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Fayl yuklash cheklovlari
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_IMAGE_UPLOAD_MB = 5

# Maxfiylik va analitika tuz kaliti
ANALYTICS_SALT = os.environ.get("ANALYTICS_SALT", SECRET_KEY[:24])

# Ruxsat etilgan tashqi xarita domenlari (Open Redirect himoyasi)
ALLOWED_GOOGLE_MAP_DOMAINS = (
    "google.com",
    "www.google.com",
    "maps.google.com",
    "goo.gl",
    "maps.app.goo.gl",
    "g.page",
    "search.google.com",
    "business.google.com",
    "google.co.uz",
    "www.google.co.uz",
)

ALLOWED_YANDEX_MAP_DOMAINS = (
    "yandex.uz",
    "www.yandex.uz",
    "yandex.com",
    "www.yandex.com",
    "yandex.ru",
    "www.yandex.ru",
    "maps.yandex.ru",
    "maps.yandex.uz",
    "ya.ru",
    "business.yandex.com",
    "business.yandex.ru",
)

# Rasmiy API adapter konfiguratsiyasi (ruxsat bo'lmasa False)
GOOGLE_BUSINESS_API_ENABLED = os.environ.get("GOOGLE_BUSINESS_API_ENABLED", "False").lower() in ("1", "true", "yes")
GOOGLE_BUSINESS_CREDENTIALS_PATH = os.environ.get("GOOGLE_BUSINESS_CREDENTIALS_PATH", "")
GOOGLE_BUSINESS_ACCOUNT_ID = os.environ.get("GOOGLE_BUSINESS_ACCOUNT_ID", "")
GOOGLE_BUSINESS_LOCATION_ID = os.environ.get("GOOGLE_BUSINESS_LOCATION_ID", "")

YANDEX_BUSINESS_API_ENABLED = os.environ.get("YANDEX_BUSINESS_API_ENABLED", "False").lower() in ("1", "true", "yes")
YANDEX_BUSINESS_API_TOKEN = os.environ.get("YANDEX_BUSINESS_API_TOKEN", "")
YANDEX_BUSINESS_ORG_ID = os.environ.get("YANDEX_BUSINESS_ORG_ID", "")

ENABLE_2FA_ENFORCEMENT = os.environ.get("ENABLE_2FA_ENFORCEMENT", "False").lower() in ("1", "true", "yes")

# Loglash sozlamalari
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
(BASE_DIR / "media").mkdir(parents=True, exist_ok=True)
STATIC_ROOT.mkdir(parents=True, exist_ok=True)

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOGS_DIR / "turon.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
            "encoding": "utf-8",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django.security": {
            "handlers": ["console", "file"],
            "level": "WARNING",
            "propagate": False,
        },
        "turon": {
            "handlers": ["console", "file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}
