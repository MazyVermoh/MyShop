# myshop/urls.py
from django.contrib import admin
from django.urls import path, include

# Для MEDIA при DEBUG
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/",    admin.site.urls),

    # ----- приложения --------------------------------------------------------
    path("",          include("store.urls")),      # витрина / каталог
    path("accounts/", include("accounts.urls")),   # регистрация / вход
    path("cart/",     include("cart.urls")),       # корзина
    path("checkout/", include("checkout.urls")),   # оформление заказа

    # ⬇️   главное: «payments» теперь содержит все эндпоинты T-Bank
    path("payments/", include("payments.urls", namespace="payments")),
]

# ----- раздача загруженных медиафайлов в режиме DEBUG -----------------------
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )