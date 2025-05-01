# checkout/views.py
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from cart.session_cart import Cart
from store.models import Order, OrderItem, Product


# ───────────────────────────────────────────────
#  Страница оформления   GET /checkout/
# ───────────────────────────────────────────────
def checkout_view(request):
    cart = Cart(request)
    if len(cart) == 0:                         # пустая корзина → назад
        return redirect("cart:detail")

    context = {
        "cart":        cart,
        "cart_total":  cart.total_price(),
    }
    return render(request, "checkout/checkout.html", context)


# ───────────────────────────────────────────────
#  Обработка формы       POST /checkout/process/
# ───────────────────────────────────────────────
@require_POST
def process_order(request):
    """
    • минимально валидируем данные
    • создаём Order + OrderItem
    • чистим корзину, редиректим на главную
    """
    cart = Cart(request)
    if len(cart) == 0:
        return redirect("cart:detail")

    # ─── 1. создаём заказ ─────────────────────────────────────────────
    order = Order.objects.create(
        first_name = request.POST.get("first_name", "Гость"),
        last_name  = request.POST.get("last_name",  ""),
        email      = request.POST.get("email",      ""),
        phone      = request.POST.get("phone",      ""),
        country    = request.POST.get("country",    ""),
        city       = request.POST.get("city",       ""),
        address    = request.POST.get("address",    ""),
        postcode   = request.POST.get("postcode",   ""),
    )

    # ─── 2. позиции заказа ────────────────────────────────────────────
    for item in cart:
        OrderItem.objects.create(
            order     = order,
            product   = item["product"],
            price     = item["product"].price,
            qty       = item["qty"],
            size      = item.get("size") or "",
            color_id  = item.get("color"),
        )

    # ─── 3. очистка корзины и редирект ────────────────────────────────
    cart.clear()
    return redirect(reverse_lazy("home"))