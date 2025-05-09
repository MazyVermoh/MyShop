from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, TemplateView, ListView, DetailView
)
from store.models import Order
from .forms import SignUpForm, CustomLoginForm

User = get_user_model()


class SignUpView(CreateView):
    form_class    = SignUpForm
    template_name = "accounts/signup.html"
    success_url   = reverse_lazy("accounts:login")


class CustomLoginView(LoginView):
    template_name               = "accounts/login.html"
    authentication_form         = CustomLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("home")


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("home")


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"
    login_url     = reverse_lazy("accounts:login")


class OrderListView(LoginRequiredMixin, ListView):
    model               = Order
    template_name       = "accounts/order_list.html"
    context_object_name = "orders"
    paginate_by         = 10
    login_url           = reverse_lazy("accounts:login")

    def get_queryset(self):
        # Показываем только заказы текущего пользователя (по email)
        return Order.objects.filter(email=self.request.user.email).order_by("-created")


class OrderDetailView(LoginRequiredMixin, DetailView):
    """
    Детали одного заказа текущего пользователя.
    URL: /account/orders/<pk>/
    """
    model               = Order
    template_name       = "accounts/order_detail.html"
    context_object_name = "order"           # ← так в шаблоне будет {{ order }}

    def get_queryset(self):
        # безопасность: отдаём ТОЛЬКО заказы текущего юзера по e‑mail
        return Order.objects.filter(email=self.request.user.email)