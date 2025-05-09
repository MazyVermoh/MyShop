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

# ────────────────────────────────────────────────────────────────────────────
# Инициализируем YooKassa SDK (разово при импорте)
# ────────────────────────────────────────────────────────────────────────────
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

    # Форма для ввода промокода
    promo_form = PromoCodeApplyForm(request.POST or None)
    discount   = Decimal("0")
    promo_code = ""

    # Обработка нажатия «Применить» в форме промокода
    if request.method == "POST" and "apply_promo" in request.POST:
        if promo_form.is_valid():
            promo_obj   = promo_form.cleaned_data["code"]       # это PromoCode instance
            promo_code  = promo_obj.code                        # строковое значение кода
            discount    = promo_obj.calculate_discount(cart.total_price())
        # если форма не валидна — ошибки покажутся автоматически

    # Считаем суммы
    cart_total  = cart.total_price()
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
    1) Читаем скрытые поля промокода и скидки.
    2) Создаём Order + OrderItem (с учётом скидки).
    3) В DEBUG — сразу перенаправляем на success.
    4) В продакшене — создаём платёж в YooKassa и редиректим туда.
    """
    cart = Cart(request)
    if len(cart) == 0:
        return redirect("cart:detail")

    # Из POST: промокод, скидка, выбор доставки и оплаты
    promo_code     = request.POST.get("promo_code", "")
    discount       = Decimal(request.POST.get("discount", "0"))
    shipping_method = request.POST.get("shipping", "")  # "courier" или "pickup"
    payment_method  = request.POST.get("payment", "")   # "card" или "yoomoney"

    # 1) Сохраняем сам заказ
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
        # Поддержки полей shipping_method/payment_method в модели пока нет —
        # можно добавить, если нужно сохранять выбор.
    )

    # 2) Сохраняем позиции из корзины
    for item in cart:
        OrderItem.objects.create(
            order    = order,
            product  = item["product"],
            price    = item["product"].price,
            qty      = item["qty"],
            size     = item.get("size") or "",
            color_id = item.get("color"),
        )

    # Рассчитываем сумму к оплате
    amount_to_pay = cart.total_price() - discount

    # 3) Если DEBUG — сразу очищаем корзину и показываем success
    if settings.DEBUG:
        cart.clear()
        return redirect(reverse_lazy("checkout:success", args=[order.id]))

    # 4) В продакшене — создаём платёж в YooKassa
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
        # Если ключи невалидны — всё равно очищаем корзину и показываем success
        cart.clear()
        return redirect(reverse_lazy("checkout:success", args=[order.id]))

    # 5) Очищаем корзину и редиректим пользователя на страницу оплаты
    cart.clear()
    return redirect(payment.confirmation.confirmation_url)


def payment_success(request, order_id):
    """
    GET /checkout/success/<order_id>/
    Пользователь вернулся из YooKassa (или DEBUG) — показываем «Спасибо».
    """
    order = Order.objects.filter(id=order_id).first()
    return render(request, "checkout/success.html", {"order": order})