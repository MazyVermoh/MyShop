# checkout/views.py
from uuid import uuid4
from decimal import Decimal

from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from yookassa import Configuration, Payment

from cart.session_cart import Cart
from store.models import Order, OrderItem, PromoCode
from .forms import PromoCodeApplyForm

# Инициализация YooKassa SDK (разово при импорте)
Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


def checkout_view(request):
    """
    GET /checkout/
    Показываем форму + краткое резюме корзины + промокод.
    Если корзина пуста → перенаправляем в cart:detail.
    """
    cart = Cart(request)
    if len(cart) == 0:
        return redirect("cart:detail")

    promo_form = PromoCodeApplyForm(request.POST or None)
    discount_amount = Decimal('0')

    # Обработка применения промокода
    if request.method == "POST" and "apply_promo" in request.POST:
        if promo_form.is_valid():
            promo = promo_form.cleaned_data["code"]
            discount_amount = promo.calculate_discount(cart.total_price())
        # даже при невалидном промокоде показываем форму с ошибками

    context = {
        "cart":        cart,
        "cart_total":  cart.total_price(),
        "promo_form":  promo_form,
        "discount":    discount_amount,
    }
    return render(request, "checkout/checkout.html", context)


@require_POST
def process_order(request):
    """
    POST /checkout/process/
    • Сохраняем Order + OrderItem
    • Если промокод валиден — прописываем discount и promo_code
    • Генерим платёж в YooKassa, редиректим на confirmation_url
    """
    cart = Cart(request)
    if len(cart) == 0:
        return redirect("cart:detail")

    # Разбор промокода
    promo = None
    discount_amount = Decimal('0')
    promo_form = PromoCodeApplyForm(request.POST)
    if promo_form.is_valid():
        promo = promo_form.cleaned_data["code"]
        discount_amount = promo.calculate_discount(cart.total_price())

    # 1) Создаём заказ со статусом pending
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
        promo_code = promo.code if promo else "",
        discount   = discount_amount,
    )

    # 2) Позиции заказа
    for item in cart:
        OrderItem.objects.create(
            order    = order,
            product  = item["product"],
            price    = item["product"].price,
            qty      = item["qty"],
            size     = item.get("size") or "",
            color_id = item.get("color"),
        )

    # 3) Создаём платёж в YooKassa
    total_to_pay = cart.total_price() - discount_amount
    if total_to_pay < 0:
        total_to_pay = Decimal('0')
    payment = Payment.create({
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
        "description": f"Заказ #{order.id} на ABUZADA STORE, сумма {total_to_pay}₽",
    }, uuid4().hex)

    # 4) Очищаем корзину и редиректим на страницу подтверждения платежа
    cart.clear()
    return redirect(payment.confirmation.confirmation_url)


def payment_success(request, order_id):
    """
    GET /checkout/success/<order_id>/
    Пользователь вернулся из YooKassa —
    показываем страницу «Спасибо за заказ».
    """
    order = Order.objects.filter(id=order_id).first()
    return render(request, "checkout/success.html", {"order": order})