from pathlib import Path
import environ

# ──────────────────────────────────────────────────────────────────────────────
# Paths & .env initialisation
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR: Path = Path(__file__).resolve().parent.parent

# Initialise environ and read .env located at project root
# If the file is missing, default values below are used.
env = environ.Env(
    # casting, default value
    DEBUG=(bool, False),
    SECRET_KEY=(str, "please_change_me"),
)

# read_env silently ignores absent file → convenient for CI
env.read_env(BASE_DIR / ".env")

# ──────────────────────────────────────────────────────────────────────────────
# Security
# ──────────────────────────────────────────────────────────────────────────────
SECRET_KEY: str = env.str("SECRET_KEY")
DEBUG: bool = env.bool("DEBUG")

# Allow all hosts in DEBUG; otherwise read from env list
if DEBUG:
    ALLOWED_HOSTS: list[str] = ["*"]
else:
    ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["example.com"])  # noqa: RUF015

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

    # local apps
    "accounts",  # кастомный пользователь
    "cart",      # сессия‑корзина
    "store",     # каталог
    "checkout",  # оформление заказа
    "payments",  # Новый слой: интеграция с платёжными шлюзами
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
        "ENGINE": env.str("DB_ENGINE", default="django.db.backends.postgresql"),
        "NAME": env.str("DB_NAME", default="myshopdb"),
        "USER": env.str("DB_USER", default="myshop"),
        "PASSWORD": env.str("DB_PASSWORD", default="password"),
        "HOST": env.str("DB_HOST", default="localhost"),
        "PORT": env.str("DB_PORT", default="5432"),
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
# Internationalisation
# ──────────────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = env.str("TIME_ZONE", default="UTC")
USE_I18N = True
USE_TZ = True

# ──────────────────────────────────────────────────────────────────────────────
# Static & Media
# ──────────────────────────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "collected_static"

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
EMAIL_HOST = env.str("EMAIL_HOST", default="smtp.mail.ru")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER", default="admin@example.com")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", default="change_me")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# URL сайта (для формирования полных ссылок)
SITE_URL = env.str("SITE_URL", default="http://localhost:8000")

# Админские адреса для системных уведомлений
ADMINS = [("Администратор", env.str("ADMIN_EMAIL", default="admin@example.com"))]

# ──────────────────────────────────────────────────────────────────────────────
# DaData
# ──────────────────────────────────────────────────────────────────────────────
DADATA_API_KEY = env.str("DADATA_API_KEY", default="")
DADATA_SECRET = env.str("DADATA_SECRET", default="")

# ──────────────────────────────────────────────────────────────────────────────
# Платежные шлюзы
# ──────────────────────────────────────────────────────────────────────────────

# T‑Bank (T‑Касса)
TBANK_TERMINAL_KEY = env.str("TBANK_TERMINAL_KEY", default="")
TBANK_PASSWORD = env.str("TBANK_PASSWORD", default="")
# "demo" | "prod"
TBANK_MODE = env.str("TBANK_MODE", default="demo")

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
