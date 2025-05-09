# myshop/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # ──────────────── Магазин ────────────────
    # 1. «Правильный» вариант — c namespace store
    path("", include(("store.urls", "store"), namespace="store")),
    # 2. Клон без namespace, чтобы старые {% url "product_detail" %} и т. п. продолжали работать
    path("", include("store.urls")),

    # ──────────────── Остальные приложения ────────────────
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("cart/",     include(("cart.urls",     "cart"),     namespace="cart")),
    path("checkout/", include(("checkout.urls", "checkout"), namespace="checkout")),
]

# Раздача MEDIA‑файлов в режиме DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)