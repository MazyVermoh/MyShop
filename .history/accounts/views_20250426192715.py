# accounts/views.py
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django import forms

User = get_user_model()

# ──────────────────────────────────────────────────────────────────────────────
# 1. Форма регистрации
# ──────────────────────────────────────────────────────────────────────────────
class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"})
    )
    password2 = forms.CharField(
        label="Повторите пароль",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"})
    )

    class Meta:
        model  = User
        fields = ("first_name", "last_name", "email", "phone", "username")

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Пароли не совпадают")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

# ──────────────────────────────────────────────────────────────────────────────
# 2. Регистрация
# ──────────────────────────────────────────────────────────────────────────────
class SignUpView(CreateView):
    form_class    = SignUpForm
    template_name = "accounts/signup.html"
    success_url   = reverse_lazy("accounts:login")

# ──────────────────────────────────────────────────────────────────────────────
# 3. Вход (кастомизированный LoginView)
# ──────────────────────────────────────────────────────────────────────────────
class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True   # уже вошедшего — на success_url
    success_url = reverse_lazy("home")   # переадресация после логина

# ──────────────────────────────────────────────────────────────────────────────
# 4. Профиль
# ──────────────────────────────────────────────────────────────────────────────
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"
    login_url     = reverse_lazy("accounts:login")