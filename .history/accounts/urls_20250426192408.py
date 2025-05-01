# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views   # SignUpView, CustomLoginView, ProfileView

app_name = "accounts"          # пространство имён: accounts:login, accounts:profile …

urlpatterns = [
    # --------------------------------------------------------------
    #  Аутентификация
    # --------------------------------------------------------------
    path(
        "login/",
        views.CustomLoginView.as_view(),   # страница «Вход»
        name="login",
    ),
    path(
        "signup/",
        views.SignUpView.as_view(),        # страница «Регистрация»
        name="signup",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="home"),
        name="logout",
    ),

    # --------------------------------------------------------------
    #  Личный кабинет
    # --------------------------------------------------------------
    path(
        "profile/",
        views.ProfileView.as_view(),
        name="profile",
    ),
]