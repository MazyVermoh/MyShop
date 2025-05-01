from django.urls import path
from .views import SignUpView, SignInView, SignOutView, ProfileView

app_name = "accounts"

urlpatterns = [
    path("sign-up/",  SignUpView.as_view(), name="sign_up"),
    path("sign-in/",  SignInView.as_view(), name="sign_in"),
    path("logout/",   SignOutView.as_view(), name="logout"),
    path("profile/",  ProfileView.as_view(), name="profile"),   # ← НОВОЕ
]