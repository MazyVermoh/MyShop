# accounts/views.py
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import SignUpForm, SignInForm


class SignUpView(FormView):
    """
    GET  → вывод формы регистрации  
    POST → создаёт пользователя и сразу авторизует его.
    """
    template_name = "accounts/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("home")          # на главную после регистрации

    def form_valid(self, form):
        user = form.save(commit=False)

        # сделаем username = email|phone, чтобы поле было непустое
        user.username = user.email or user.phone
        user.save()

        # автоматический вход после регистрации
        login(self.request, user)
        return super().form_valid(form)


class SignInView(LoginView):
    """
    Стандартный LoginView, но с нашей формой и шаблоном.
    """
    template_name = "accounts/signin.html"
    authentication_form = SignInForm
    redirect_authenticated_user = True          # если уже вошёл — на success_url
    success_url = reverse_lazy("home")


class SignOutView(LogoutView):
    """
    Выход из аккаунта → редирект на главную.
    """
    next_page = reverse_lazy("home")