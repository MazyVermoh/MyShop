# checkout/views.py

from uuid import uuid4
from decimal import Decimal

from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from yookassa import Configuration, Payment
from yookassa.domain.exceptions.unauthorized_error import UnauthorizedError

from cart.session_cart import Cart
from store.models import Order, OrderItem
from .forms import PromoCodeApplyForm
from .utils import send_order_confirmation, notify_admin_new_order

from django.shortcuts import get_object_or_404

# ────────────────────────────────────────────────────────────────────────────
# Инициализируем YooKassa SDK (при импорте модуля)
# ────────────────────────────────────────────────────────────────────────────
Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


def checkout_view(request):
    """
    GET  /checkout/               — показываем форму + резюме корзины
    POST /checkout/ (apply_promo) — применяем промокод, пересчитываем скидку
    """
    cart = Cart(request)
    if len(cart) == 0:
        return redirect("cart:detail")

    promo_form = PromoCodeApplyForm(request.POST or None)
    discount = Decimal("0")
    promo_code = ""

    # если нажали «Применить промокод»
    if request.method == "POST" and "apply_promo" in request.POST:
        if promo_form.is_valid():
            promo_obj = promo_form.cleaned_data["code"]  # это instance PromoCode
            promo_code = promo_obj.code
            discount = promo_obj.calculate_discount(cart.total_price())
        # при невалидности form.errors покажутся в шаблоне

    cart_total = cart.total_price()
    final_total = cart_total - discount

    return render(request, "checkout/checkout.html", {
        "cart":        cart,
        "cart_total":  cart_total,
        "promo_form":  promo_form,
        "discount":    discount,
        "promo_code":  promo_code,
        "final_total": final_total,
    })


@require_POST
def process_order(request):
    """
    POST /checkout/process/:
      1) Сохраняем Order и OrderItem (с учётом промокода/скидки/способов).
      2) Отправляем письма клиенту и админу.
      3) В DEBUG — сразу переходим на success.
      4) Иначе — создаём платёж в YooKassa и редиректим туда.
    """
    cart = Cart(request)
    if len(cart) == 0:
        return redirect("cart:detail")

    # читаем скрытые поля из формы
    promo_code      = request.POST.get("promo_code", "")
    discount        = Decimal(request.POST.get("discount", "0"))
    shipping_method = request.POST.get("shipping", "")
    payment_method  = request.POST.get("payment", "")

    # 1) создаём заказ
    order = Order.objects.create(
        status          = "pending",
        first_name      = request.POST.get("first_name", ""),
        last_name       = request.POST.get("last_name", ""),
        email           = request.POST.get("email", ""),
        phone           = request.POST.get("phone", ""),
        country         = request.POST.get("country", ""),
        city            = request.POST.get("city", ""),
        address         = request.POST.get("address", ""),
        postcode        = request.POST.get("postcode", ""),
        promo_code      = promo_code,
        discount        = discount,
        shipping_method = shipping_method,
        payment_method  = payment_method,
    )

    # 2) сохраняем позиции заказа
    for item in cart:
        OrderItem.objects.create(
            order    = order,
            product  = item["product"],
            price    = item["product"].price,
            qty      = item["qty"],
            size     = item.get("size") or "",
            color_id = item.get("color"),
        )

    # 3) отправляем e-mail уведомления
    send_order_confirmation(order)
    notify_admin_new_order(order)

    # 4) если DEBUG — сразу показываем страницу «Спасибо»
    if settings.DEBUG:
        redirect_url = reverse_lazy("checkout:success", args=[order.id])
    else:
        # иначе постепенно создаём платёж в YooKassa
        total_to_pay = cart.total_price() - discount
        try:
            payment = Payment.create(
                {
                    "amount": {
                        "value":    f"{total_to_pay:.2f}",
                        "currency": "RUB",
                    },
                    "confirmation": {
                        "type":       "redirect",
                        "return_url": request.build_absolute_uri(
                            reverse_lazy("checkout:success", args=[order.id])
                        ),
                    },
                    "capture":     True,
                    "description": f"Заказ #{order.id}, сумма {total_to_pay}₽",
                },
                uuid4().hex
            )
            redirect_url = payment.confirmation.confirmation_url
        except UnauthorizedError:
            # при ошибке с ключами — показываем success
            redirect_url = reverse_lazy("checkout:success", args=[order.id])

    # 5) очищаем корзину и редиректим
    cart.clear()
    return redirect(redirect_url)


def payment_success(request, order_id):
    """
    GET /checkout/success/<order_id>/
    — показываем страницу «Спасибо за заказ»
    """
    order = Order.objects.filter(id=order_id).first()
    return render(request, "checkout/success.html", {"order": order})

def order_status(request, order_id):
    """
    GET /checkout/status/<order_id>/
    Показываем клиенту текущий статус его заказа.
    """
    order = get_object_or_404(Order, id=order_id)
    return render(request, "checkout/order_status.html", {
        "order": order,
    })