from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import SignUpView, SignInView, ProfileView

app_name = "accounts"

urlpatterns = [
    path("login/",  SignInView.as_view(),  name="login"),
    path("signup/", SignUpView.as_view(), name="signup"),
    # при выходе сразу отправляем на главную
    path("logout/", LogoutView.as_view(next_page="home"), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
]