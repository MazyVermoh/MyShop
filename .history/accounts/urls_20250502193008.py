# accounts/urls.py
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # ─────────── регистрация / вход ───────────
    path("signup/", views.SignUpView.as_view(),        name="signup"),
    path("login/",  views.CustomLoginView.as_view(),   name="login"),

    # ─────────── выход (редирект на HOME) ─────
    path(
        "logout/",
        views.CustomLogoutView.as_view(),              # next_page берём из класса
        name="logout",
    ),

    # ─────────── личный кабинет ────────────────
    path("profile/", views.ProfileView.as_view(),      name="profile"),
    # Список всех заказов текущего пользователя
    path("orders/", views.OrderListView.as_view(), name="order_list"),
    # Детали одного заказа
    path("orders/<int:pk>/", views.OrderDetailView.as_view(), name="order_detail"),
]