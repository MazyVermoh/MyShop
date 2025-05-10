"""
Django settings for *myshop* project.
Production‑ready version.
All секреты и окружение берутся из `.env` (см. `.env.example`).
"""

from pathlib import Path
import os
import environ

# ──────────────────────────────────────────────────────────────────────────────
# Paths & base dir
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR: Path = Path(__file__).resolve().parent.parent

# ──────────────────────────────────────────────────────────────────────────────
# Environment variables (.env)
# ──────────────────────────────────────────────────────────────────────────────
# Указываем дефолты только там, где это безопасно
env = environ.Env(
    DJANGO_DEBUG=(bool, False),
)
# читаем .env, если есть
env_path = BASE_DIR / ".env"
if env_path.exists():
    environ.Env.read_env(env_path)

# ──────────────────────────────────────────────────────────────────────────────
# Security
# ──────────────────────────────────────────────────────────────────────────────
SECRET_KEY: str = env("DJANGO_SECRET_KEY")
DEBUG: bool = env("DJANGO_DEBUG")
ALLOWED_HOSTS: list[str] = env.list("ALLOWED_HOSTS")

# Jino‑proxy передаёт этот заголовок, если запрос пришёл по HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ──────────────────────────────────────────────────────────────────────────────
# Applications
# ──────────────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # project apps
    "checkout",
    "store",
    "accounts",
]

# ──────────────────────────────────────────────────────────────────────────────
# Middleware / URLs / WSGI
# ──────────────────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "myshop.urls"
WSGI_APPLICATION = "myshop.wsgi.application"

# ──────────────────────────────────────────────────────────────────────────────
# Templates
# ──────────────────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "cart.context_processors.cart_totals",
            ],
        },
    },
]

# ──────────────────────────────────────────────────────────────────────────────
# Database
# ──────────────────────────────────────────────────────────────────────────────
DATABASES = {
    "default": env.db(),  # DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/DB
}

# ──────────────────────────────────────────────────────────────────────────────
# Password validation
# ──────────────────────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ──────────────────────────────────────────────────────────────────────────────
# Internationalization
# ──────────────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ──────────────────────────────────────────────────────────────────────────────
# Static & media
# ──────────────────────────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ──────────────────────────────────────────────────────────────────────────────
# Custom user model
# ──────────────────────────────────────────────────────────────────────────────
AUTH_USER_MODEL = "accounts.User"

# ──────────────────────────────────────────────────────────────────────────────
# Login / Logout redirects
# ──────────────────────────────────────────────────────────────────────────────
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "home"

# ──────────────────────────────────────────────────────────────────────────────
# Cart session key
# ──────────────────────────────────────────────────────────────────────────────
CART_SESSION_KEY = "cart"

# ──────────────────────────────────────────────────────────────────────────────
# Email (SMTP)
# ──────────────────────────────────────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="smtp.mail.ru")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

SITE_URL = env("SITE_URL", default="https://example.com")

ADMINS = [("Administrator", env("ADMIN_EMAIL", default="admin@example.com"))]

# ──────────────────────────────────────────────────────────────────────────────
# DaData
# ──────────────────────────────────────────────────────────────────────────────
DADATA_API_KEY = env("DADATA_API_KEY", default="")
# DADATA_SECRET = env("DADATA_SECRET", default="")

# ──────────────────────────────────────────────────────────────────────────────
# YooKassa
# ──────────────────────────────────────────────────────────────────────────────
YOOKASSA_SHOP_ID = env("YOOKASSA_SHOP_ID", default="")
YOOKASSA_SECRET_KEY = env("YOOKASSA_SECRET_KEY", default="")

# ──────────────────────────────────────────────────────────────────────────────
# Authentication backends
# ──────────────────────────────────────────────────────────────────────────────
AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailPhoneUsernameBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# ──────────────────────────────────────────────────────────────────────────────
# Default primary key field type
# ──────────────────────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"