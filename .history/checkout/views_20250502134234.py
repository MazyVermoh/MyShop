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


# 1) Инициализируем SDK YooKassa (разово при импорте модуля)
Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


def checkout_view(request):
    """
    GET  /checkout/            — показать форму оформления + резюме корзины
    POST /checkout/ (apply_promo) — применить промокод и пересчитать скидку
    """
    cart = Cart(request)
    if len(cart) == 0:
        return redirect("cart:detail")

    # Форма для промокода
    promo_form = PromoCodeApplyForm(request.POST or None)
    discount = Decimal("0")
    applied_code = ""

    # Если нажали «Применить промокод» — проверяем его
    if request.method == "POST" and "apply_promo" in request.POST:
        if promo_form.is_valid():
            applied_code = promo_form.cleaned_data["code"]
            # Предполагаем, что у вас в модели PromoCode есть метод calculate_discount
            # discount = promo_obj.calculate_discount(cart.total_price())
            # Для простоты: пусть form сам считает скидку
            discount = promo_form.get_discount(cart.total_price())
        # Если форма невалидна, ошибки будут показаны в шаблоне

    return render(request, "checkout/checkout.html", {
        "cart":        cart,
        "cart_total":  cart.total_price(),
        "promo_form":  promo_form,
        "discount":    discount,
        "promo_code":  applied_code,
    })


@require_POST
def process_order(request):
    """
    POST /checkout/process/
    • Создаём Order + OrderItem (с учётом промокода и скидки).
    • В DEBUG режиме — сразу редиректим на страницу успеха.
    • В продакшене — создаём платёж в YooKassa и редиректим на confirmation_url.
    """
    cart = Cart(request)
    if len(cart) == 0:
        return redirect("cart:detail")

    # Читаем промокод и скидку из скрытых полей формы
    promo_code = request.POST.get("promo_code", "")
    discount = Decimal(request.POST.get("discount", "0"))

    # 1) сохраняем заказ
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

    # 3) в режиме отладки сразу помечаем как оплаченный
    if settings.DEBUG:
        cart.clear()
        return redirect(reverse_lazy("checkout:success", args=[order.id]))

    # 4) иначе — создаём платёж в YooKassa
    total_amount = cart.total_price() - discount
    try:
        payment = Payment.create({
            "amount": {
                "value":    f"{total_amount:.2f}",
                "currency": "RUB",
            },
            "confirmation": {
                "type":       "redirect",
                "return_url": request.build_absolute_uri(
                                  reverse_lazy("checkout:success", args=[order.id])
                              )
            },
            "capture":     True,
            "description": f"Заказ #{order.id}, сумма {total_amount}₽",
        }, uuid4().hex)
    except UnauthorizedError:
        # Если неверные ключи — просто перекидываем на «Спасибо» (можно залогировать)
        cart.clear()
        return redirect(reverse_lazy("checkout:success", args=[order.id]))

    # 5) чистим корзину и редиректим на страницу оплаты YooKassa
    cart.clear()
    return redirect(payment.confirmation.confirmation_url)


def payment_success(request, order_id):
    """
    GET /checkout/success/<order_id>/
    Пользователь вернулся после оплаты — показываем «Спасибо».
    Статус можно обновить через Webhook.
    """
    order = Order.objects.filter(id=order_id).first()
    return render(request, "checkout/success.html", {"order": order})