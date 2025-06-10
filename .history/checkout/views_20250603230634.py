# checkout/views.py
from decimal import Decimal

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from cart.session_cart import Cart
from store.models import Order, OrderItem
from .forms import PromoCodeApplyForm
from .utils import notify_admin_new_order, send_order_confirmation


# ────────────────────────────────────────────────────────────
# 1.  GET /checkout/  — форма + применение промокода
# ────────────────────────────────────────────────────────────
def checkout_view(request: HttpRequest) -> HttpResponse:
    cart = Cart(request)
    if not cart:
        return redirect("cart:detail")

    promo_form = PromoCodeApplyForm(request.POST or None)
    discount = Decimal("0")
    promo_code = ""

    # пользователь нажал «Применить»
    if request.method == "POST" and "apply_promo" in request.POST:
        if promo_form.is_valid():
            promo_obj = promo_form.cleaned_data["code"]
            promo_code = promo_obj.code
            discount = promo_obj.calculate_discount(cart.total_price())

    cart_total   = cart.total_price()
    shipping_fee = Decimal("0")          # ПВЗ по умолчанию
    final_total  = cart_total - discount # без доставки

    context = {
        "cart": cart,
        "cart_total": cart_total,
        "promo_form": promo_form,
        "discount": discount,
        "promo_code": promo_code,
        "final_total": final_total,
        "DADATA_SUGGESTIONS_KEY": settings.DADATA_API_KEY,
    }
    return render(request, "checkout/checkout.html", context)


# ────────────────────────────────────────────────────────────
# 2.  POST /checkout/process/  — создаём заказ
# ────────────────────────────────────────────────────────────
@require_POST
def process_order(request: HttpRequest) -> HttpResponse:
    cart = Cart(request)
    if not cart:
        return redirect("cart:detail")

    # --- данные из формы ------------------------------------------------------
    promo_code      = request.POST.get("promo_code", "")
    discount        = Decimal(request.POST.get("discount", "0"))
    shipping_method = request.POST.get("shipping", "courier")
    payment_method  = request.POST.get("payment", "card")
    telegram_handle = request.POST.get("telegram", "").lstrip("@")

    shipping_fee = Decimal("600.00") if shipping_method == "courier" else Decimal("0")

    # --- создаём Order --------------------------------------------------------
    order = Order.objects.create(
        user           = request.user if request.user.is_authenticated else None,
        status         = "pending",
        first_name     = request.POST.get("first_name", ""),
        last_name      = request.POST.get("last_name", ""),
        email          = request.POST.get("email", ""),
        phone          = request.POST.get("phone", ""),
        telegram       = telegram_handle,
        country        = request.POST.get("country", ""),
        city           = request.POST.get("city", ""),
        address        = request.POST.get("address", ""),
        postcode       = request.POST.get("postcode", ""),
        promo_code     = promo_code,
        discount       = discount,
        shipping_method= shipping_method,
        shipping_price = shipping_fee,
        payment_method = payment_method,
    )

    for item in cart:
        OrderItem.objects.create(
            order   = order,
            product = item["product"],
            price   = item["product"].price,
            qty     = item["qty"],
            size    = item.get("size") or "",
            color_id= item.get("color"),
        )

    # --- письма ---------------------------------------------------------------
    send_order_confirmation(order)
    notify_admin_new_order(order)

    cart.clear()  # корзина пуста

    # ─── если выбрана оплата картой → редирект на платежку ────────────────────
    if payment_method == "card":
        # payments:tbank_start → payments/urls.py
        return redirect("payments:tbank_start", order_id=order.id)

    # ─── «Оплата при получении» или иное ──────────────────────────────────────
    return redirect(reverse("checkout:success", args=[order.id]))


# ────────────────────────────────────────────────────────────
# 3.  /checkout/success/<order_id>/
# ────────────────────────────────────────────────────────────
def payment_success(request: HttpRequest, order_id: int) -> HttpResponse:
    order = get_object_or_404(Order, id=order_id)
    return render(request, "checkout/success.html", {"order": order})


# ────────────────────────────────────────────────────────────
# 4.  /checkout/failure/<order_id>/  (для FailURL банка)
# ────────────────────────────────────────────────────────────
def payment_failure(request: HttpRequest, order_id: int) -> HttpResponse:
    order = get_object_or_404(Order, id=order_id)
    return render(request, "checkout/failure.html", {"order": order})


# ────────────────────────────────────────────────────────────
# 5.  /checkout/status/<order_id>/  — личный кабинет
# ────────────────────────────────────────────────────────────
def order_status(request: HttpRequest, order_id: int) -> HttpResponse:
    order       = get_object_or_404(Order, id=order_id)
    items       = order.items.all()
    items_total = sum(item.total() for item in items)

    context = {
        "order": order,
        "items": items,
        "items_total": items_total,
    }
    return render(request, "checkout/order_status.html", context)