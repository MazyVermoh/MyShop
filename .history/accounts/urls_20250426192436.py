from django.urls import path
from django.contrib.auth import views as auth_views
from . import views          # SignUpView, ProfileView

app_name = "accounts"

urlpatterns = [
    # ---------- ВХОД -----------
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html"   # ваш шаблон формы входа
        ),
        name="login",
    ),

    # ---------- РЕГИСТРАЦИЯ ----
    path("signup/",  views.SignUpView.as_view(),  name="signup"),

    # ---------- ВЫХОД ----------
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="home"),
        name="logout",
    ),

    # ---------- ПРОФИЛЬ --------
    path("profile/", views.ProfileView.as_view(), name="profile"),
]