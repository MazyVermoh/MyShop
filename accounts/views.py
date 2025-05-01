# accounts/views.py
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import SignUpForm, CustomLoginForm

User = get_user_model()


# ──────────────────────────────────────────────────────────────────
# 1. Регистрация
# ──────────────────────────────────────────────────────────────────
class SignUpView(CreateView):
    form_class    = SignUpForm
    template_name = "accounts/signup.html"
    success_url   = reverse_lazy("accounts:login")


# ──────────────────────────────────────────────────────────────────
# 2. Вход
# ──────────────────────────────────────────────────────────────────
class CustomLoginView(LoginView):
    template_name               = "accounts/login.html"
    authentication_form         = CustomLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("home")


# ──────────────────────────────────────────────────────────────────
# 3. Выход — просто редиректим на главную
# ──────────────────────────────────────────────────────────────────
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("home")


# ──────────────────────────────────────────────────────────────────
# 4. Профиль (виден только авторизованным)
# ──────────────────────────────────────────────────────────────────
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"
    login_url     = reverse_lazy("accounts:login")