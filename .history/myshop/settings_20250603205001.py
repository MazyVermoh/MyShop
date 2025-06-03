"""
Django settings for myshop project.
Параметризованы через .env (django‑environ).
Файл рассчитан на интеграцию с T‑Bank.
"""

from pathlib import Path
import environ

# ──────────────────────────────────────────────────────────────────────────────
# Paths & env
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR: Path = Path(__file__).resolve().parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_SECRET_KEY=(str, "please_change_me"),
)
# silent=True → CI не падает без .env
env.read_env(BASE_DIR / ".env", overwrite=False)

# ──────────────────────────────────────────────────────────────────────────────
# Security
# ──────────────────────────────────────────────────────────────────────────────
SECRET_KEY: str = env.str("DJANGO_SECRET_KEY")
DEBUG: bool = env.bool("DJANGO_DEBUG")

if DEBUG:
    ALLOWED_HOSTS: list[str] = ["*"]
else:
    ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["example.com"])

# ──────────────────────────────────────────────────────────────────────────────
# Installed apps
# ──────────────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # local apps
    "accounts",
    "cart",
    "store",
    "checkout",
    "payments",  # NEW
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
    "default": {
        "ENGINE": env.str("DB_ENGINE", "django.db.backends.postgresql"),
        "NAME": env.str("DB_NAME", "myshopdb"),
        "USER": env.str("DB_USER", "myshop"),
        "PASSWORD": env.str("DB_PASSWORD", "password"),
        "HOST": env.str("DB_HOST", "localhost"),
        "PORT": env.int("DB_PORT", 5432),
    }
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
# i18n / tz
# ──────────────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = env.str("TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

# ──────────────────────────────────────────────────────────────────────────────
# Static / media
# ──────────────────────────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "collected_static"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ──────────────────────────────────────────────────────────────────────────────
# Auth
# ──────────────────────────────────────────────────────────────────────────────
AUTH_USER_MODEL = "accounts.User"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "home"
AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailPhoneUsernameBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# ──────────────────────────────────────────────────────────────────────────────
# Misc consts
# ──────────────────────────────────────────────────────────────────────────────
CART_SESSION_KEY = "cart"

# ──────────────────────────────────────────────────────────────────────────────
# Email
# ──────────────────────────────────────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env.str("EMAIL_HOST", "smtp.mail.ru")
EMAIL_PORT = env.int("EMAIL_PORT", 587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", True)
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER", "admin@example.com")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", "change_me")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SITE_URL = env.str("SITE_URL", "http://localhost:8000")
ADMINS = [("Администратор", env.str("ADMIN_EMAIL", "admin@example.com"))]

# ──────────────────────────────────────────────────────────────────────────────
# DaData
# ──────────────────────────────────────────────────────────────────────────────
DADATA_API_KEY = env.str("DADATA_API_KEY", "")
DADATA_SECRET = env.str("DADATA_SECRET", "")

# ──────────────────────────────────────────────────────────────────────────────
# Payment gateways
# ──────────────────────────────────────────────────────────────────────────────
TBANK_TERMINAL_KEY = env.str("TBANK_TERMINAL_KEY", "")
TBANK_PASSWORD = env.str("TBANK_PASSWORD", "")
TBANK_MODE = env.str("TBANK_MODE", "demo")  # demo | prod

# ──────────────────────────────────────────────────────────────────────────────
# Django
# ──────────────────────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
