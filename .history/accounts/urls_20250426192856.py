# accounts/urls.py
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # регистрация / вход
    path("signup/", views.SignUpView.as_view(),   name="signup"),
    path("login/",  views.CustomLoginView.as_view(), name="login"),

    # выход – сразу редиректим на главную
    path(
        "logout/",
        views.CustomLogoutView.as_view(next_page="home"),
        name="logout",
    ),

    # личный кабинет
    path("profile/", views.ProfileView.as_view(), name="profile"),
]