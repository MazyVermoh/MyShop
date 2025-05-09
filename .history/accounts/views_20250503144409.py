# accounts/views.py
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, ListView, DetailView

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


# ────────────────────────────────
# Профиль
# ────────────────────────────────
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"
    login_url     = reverse_lazy("accounts:login")

    # ► заполняем статистику заказов
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        orders_qs           = self.request.user.orders.order_by("-created")
        ctx["orders_count"] = orders_qs.count()
        ctx["last_order"]   = orders_qs.first()
        return ctx


# ────────────────────────────────
# История заказов
# ────────────────────────────────
class OrderListView(LoginRequiredMixin, ListView):
    model               = Order
    template_name       = "accounts/order_list.html"
    context_object_name = "orders"
    paginate_by         = 10
    login_url           = reverse_lazy("accounts:login")

    # теперь фильтруем по FK‑связи user
    def get_queryset(self):
        return self.request.user.orders.order_by("-created")


# ────────────────────────────────
# Детали конкретного заказа
# ────────────────────────────────
class OrderDetailView(LoginRequiredMixin, DetailView):
    model               = Order
    template_name       = "accounts/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return self.request.user.orders.all()

    # ► добавляем items и их сумму
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        items              = self.object.items.all()
        ctx["items"]       = items
        ctx["items_total"] = sum(it.total() for it in items)
        return ctx