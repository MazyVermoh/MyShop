# checkout/views.py
from uuid import uuid4
from decimal import Decimal

from django.conf          import settings
from django.shortcuts     import render, redirect, get_object_or_404
from django.urls          import reverse_lazy
from django.views.decorators.http import require_POST

from yookassa import Configuration, Payment
from yookassa.domain.exceptions.unauthorized_error import UnauthorizedError

from cart.session_cart   import Cart
from store.models        import Order, OrderItem
from .forms              import PromoCodeApplyForm
from .utils              import send_order_confirmation, notify_admin_new_order


# ────────────────────────────────────────────────
# Инициализируем YooKassa SDK
# ────────────────────────────────────────────────
Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


# ────────────────────────────────────────────────
# 1. Страница /checkout/
# ────────────────────────────────────────────────
def checkout_view(request):
    cart = Cart(request)
    if not cart:
        return redirect("cart:detail")

    promo_form  = PromoCodeApplyForm(request.POST or None)
    discount    = Decimal("0")
    promo_code  = ""

    # «Применить промокод»
    if request.method == "POST" and "apply_promo" in request.POST:
        if promo_form.is_valid():
            promo_obj  = promo_form.cleaned_data["code"]
            promo_code = promo_obj.code
            discount   = promo_obj.calculate_discount(cart.total_price())

    cart_total      = cart.total_price()
    shipping_price  = Decimal("0")            # по умолчанию – ПВЗ
    final_total     = cart_total - discount   # цена без доставки (обновится на POST)

    return render(request, "checkout/checkout.html", {
        "cart":        cart,
        "cart_total":  cart_total,
        "promo_form":  promo_form,
        "discount":    discount,
        "promo_code":  promo_code,
        "final_total": final_total,
    })


# ────────────────────────────────────────────────
# 2. POST /checkout/process/
# ────────────────────────────────────────────────
@require_POST
def process_order(request):
    cart = Cart(request)
    if not cart:
        return redirect("cart:detail")

    # ─── читаем поля формы ───
    promo_code      = request.POST.get("promo_code", "")
    discount        = Decimal(request.POST.get("discount", "0"))
    shipping_method = request.POST.get("shipping", "courier")
    payment_method  = request.POST.get("payment", "card")
    telegram_handle = request.POST.get("telegram", "").lstrip("@")

    # стоимость доставки
    shipping_price = Decimal("600.00") if shipping_method == "courier" else Decimal("0")

    # ─── Order ───
    order = Order.objects.create(
        user            = request.user if request.user.is_authenticated else None,
        status          = "pending",
        first_name      = request.POST.get("first_name", ""),
        last_name       = request.POST.get("last_name", ""),
        email           = request.POST.get("email", ""),
        phone           = request.POST.get("phone", ""),
        telegram        = telegram_handle,
        country         = request.POST.get("country", ""),
        city            = request.POST.get("city", ""),
        address         = request.POST.get("address", ""),
        postcode        = request.POST.get("postcode", ""),
        promo_code      = promo_code,
        discount        = discount,
        shipping_method = shipping_method,
        shipping_price  = shipping_price,
        payment_method  = payment_method,
    )

    # ─── позиции ───
    for item in cart:
        OrderItem.objects.create(
            order    = order,
            product  = item["product"],
            price    = item["product"].price,
            qty      = item["qty"],
            size     = item.get("size") or "",
            color_id = item.get("color"),
        )

    # ─── e‑mail уведомления ───
    send_order_confirmation(order)
    notify_admin_new_order(order)

    # Итог к оплате
    total_to_pay = cart.total_price() + shipping_price - discount

    # ─── куда редиректить ───
    if settings.DEBUG:
        redirect_url = reverse_lazy("checkout:success", args=[order.id])
    else:
        try:
            payment = Payment.create(
                {
                    "amount": {"value": f"{total_to_pay:.2f}", "currency": "RUB"},
                    "confirmation": {
                        "type": "redirect",
                        "return_url": request.build_absolute_uri(
                            reverse_lazy("checkout:success", args=[order.id])
                        ),
                    },
                    "capture": True,
                    "description": f"Заказ #{order.id}, сумма {total_to_pay}₽",
                },
                uuid4().hex,
            )
            redirect_url = payment.confirmation.confirmation_url
        except UnauthorizedError:
            redirect_url = reverse_lazy("checkout:success", args=[order.id])

    cart.clear()
    return redirect(redirect_url)


# ────────────────────────────────────────────────
# 3. /checkout/success/<order_id>/
# ────────────────────────────────────────────────
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "checkout/success.html", {"order": order})


# ────────────────────────────────────────────────
# 4. /checkout/status/<order_id>/
# ────────────────────────────────────────────────
def order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all()
    items_total = sum(i.total() for i in items)

    return render(request, "checkout/order_status.html", {
        "order":       order,
        "items":       items,
        "items_total": items_total,
    })