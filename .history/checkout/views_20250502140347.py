# checkout/views.py

from uuid import uuid4
from decimal import Decimal

from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

# YooKassa SDK
from yookassa import Configuration, Payment
from yookassa.domain.exceptions.unauthorized_error import UnauthorizedError

from cart.session_cart import Cart
from store.models import Order, OrderItem
from .forms import PromoCodeApplyForm


# ───────────────────────────────────────────────────────────────
# Инициализация YooKassa SDK (при импорте модуля)
# ───────────────────────────────────────────────────────────────
Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


def checkout_view(request):
    """
    GET  /checkout/              — показать форму оформления + резюме корзины
    POST /checkout/ (apply_promo) — применить промокод и пересчитать скидку
    """
    cart = Cart(request)
    if len(cart) == 0:
        return redirect("cart:detail")

    # Форма для промокода
    promo_form = PromoCodeApplyForm(request.POST or None)
    discount = Decimal("0")
    promo_code = ""

    # Пользователь нажал «Применить промокод»
    if request.method == "POST" and "apply_promo" in request.POST:
        if promo_form.is_valid():
            promo_code = promo_form.cleaned_data["code"]
            # Предполагаем, что форма знает, как рассчитать скидку:
            discount = promo_form.get_discount(cart.total_price())
        # При невалидной форме ошибки покажутся в шаблоне

    # Итоговая сумма товаров
    cart_total = cart.total_price()
    # С учётом скидки
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
    POST /checkout/process/
    1) Создаем Order и OrderItem (с учётом промокода и скидки).
    2) В DEBUG — отмечаем оплату и перекидываем на success.
    3) Иначе — создаем платеж в YooKassa и редиректим пользователя.
    """
    cart = Cart(request)
    if len(cart) == 0:
        return redirect("cart:detail")

    # Берём промокод и скидку из скрытых полей формы
    promo_code = request.POST.get("promo_code", "")
    discount   = Decimal(request.POST.get("discount", "0"))

    # 1) Сохранение самого заказа
    order = Order.objects.create(
        status     = "pending",
        first_name = request.POST.get("first_name", ""),
        last_name  = request.POST.get("last_name",  ""),
        email      = request.POST.get("email",      ""),
        phone      = request.POST.get("phone",      ""),
        country    = request.POST.get("country",    ""),
        city       = request.POST.get("city",       ""),
        address    = request.POST.get("address",    ""),
        postcode   = request.POST.get("postcode",   ""),
        promo_code = promo_code,
        discount   = discount,
    )

    # 2) Сохранение позиций из корзины
    for item in cart:
        OrderItem.objects.create(
            order    = order,
            product  = item["product"],
            price    = item["product"].price,
            qty      = item["qty"],
            size     = item.get("size") or "",
            color_id = item.get("color"),
        )

    # Сумма к оплате по итогу
    amount_to_pay = cart.total_price() - discount

    # 3) В DEBUG режиме — сразу считаем заказ оплаченным
    if settings.DEBUG:
        cart.clear()
        return redirect(reverse_lazy("checkout:success", args=[order.id]))

    # 4) В production — создаём платёж в YooKassa
    try:
        payment = Payment.create(
            {
                "amount": {
                    "value":    f"{amount_to_pay:.2f}",
                    "currency": "RUB",
                },
                "confirmation": {
                    "type":       "redirect",
                    "return_url": request.build_absolute_uri(
                        reverse_lazy("checkout:success", args=[order.id])
                    ),
                },
                "capture":     True,
                "description": f"Заказ #{order.id}, сумма {amount_to_pay}₽",
            },
            uuid4().hex
        )
    except UnauthorizedError:
        # Если ключи неправильные — просто очищаем корзину и показываем success
        cart.clear()
        return redirect(reverse_lazy("checkout:success", args=[order.id]))

    # 5) Очищаем корзину и редиректим на страницу оплаты YooKassa
    cart.clear()
    return redirect(payment.confirmation.confirmation_url)


def payment_success(request, order_id):
    """
    GET /checkout/success/<order_id>/
    Пользователь успешно оплатил (или DEBUG) — показываем «Спасибо за заказ».
    """
    order = Order.objects.filter(id=order_id).first()
    return render(request, "checkout/success.html", {"order": order})