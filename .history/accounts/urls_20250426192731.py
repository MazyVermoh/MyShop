# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views

from .views import CustomLoginView, SignUpView, ProfileView

app_name = "accounts"          # пространство имён: accounts:login и др.

urlpatterns: list[path] = [
    # ───────────────────────────────────────────
    #   Аутентификация
    # ───────────────────────────────────────────
    path(
        "login/",
        CustomLoginView.as_view(),          # страница «Вход»
        name="login",
    ),
    path(
        "signup/",
        SignUpView.as_view(),               # страница «Регистрация»
        name="signup",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="home"),   # выход и редирект на главную
        name="logout",
    ),

    # ───────────────────────────────────────────
    #   Личный кабинет
    # ───────────────────────────────────────────
    path(
        "profile/",
        ProfileView.as_view(),              # страница «Профиль»
        name="profile",
    ),
]